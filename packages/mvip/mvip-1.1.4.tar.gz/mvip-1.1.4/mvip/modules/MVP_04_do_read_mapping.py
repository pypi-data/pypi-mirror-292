import argparse
import os
import subprocess
import glob
import pandas as pd
from functools import reduce
import datetime
import time
import mvip

def fetch_arguments(parser):
    parser.set_defaults(func=main)
    parser.set_defaults(program="MVP_04_do_read_mapping")
    parser.add_argument(
        "--input", "-i",
        help="Path to your working directory where you want to run MVP.",
    )
    parser.add_argument(
        "--metadata", "-m",
        help="Path to your metadata that you want to use to run MVP.",
    )
    parser.add_argument(
        "--sample_group",
        help="Specific sample number(s) to run the script on (can be a comma-separated list: 1,2,6 for example). By default, MVP processes all datasets listed in the metadata file one after the other.",
    )
    parser.add_argument(
        "--force_read_mapping",
        action='store_true',
        help="Do the read mapping even if outputs already exist.",
    )
    parser.add_argument(
        "--read_type",
        type=str,
        default='short',
        help="Sequencing data type (e.g. short vs long reads). Default = short.",
    )
    parser.add_argument(
        "--interleaved",
        type=str,
        default='TRUE',
        help="Enable or disable the --interleaved option in Bowtie2 command (TRUE/FALSE).",
    )
    parser.add_argument(
        "--delete_files",
        action='store_true',
        help="flag to delete unwanted files.",
    )
    parser.add_argument(
        '--threads', 
        type=int,
        default=1,
        help='Number of threads to use (default = 1)')

class StepCounter:
    def __init__(self):
        self.current_step = 0
        self.current_substep = 'A'

    def print_main_step(self):
        self.current_step += 1
        self.current_substep = 'A'  # Reset sub-step counter to 'A'
        return f"Step {self.current_step}"

    def print_sub_step(self):
        if self.current_substep == 'A':  # Only increment main step if starting a new sub-step series
            main_step = self.print_main_step()
        else:
            main_step = f"Step {self.current_step}"  # Use current main step without incrementing
        sub_step = self.current_substep
        self.current_substep = chr(ord(self.current_substep) + 1)
        return f"{main_step}{sub_step}"
    
    def reset(self):
        self.current_step = 0
        self.current_substep = 'A'

# Example usage:
step_counter = StepCounter()

def read_mapping(args, sample_name, input_fastq, row):
    # Create directories for the current sample in 01_GENOMAD and 02_CHECK_V
    read_mapping_sample_directory = os.path.join(args['input'], '04_READ_MAPPING', str(row['Sample']))
    os.makedirs(read_mapping_sample_directory, exist_ok=True)

    reference_path = os.path.join(args['input'], '04_READ_MAPPING', 'reference')
    output_sam = os.path.join(read_mapping_sample_directory, str(sample_name) + '.sam')
    output_bam = os.path.join(read_mapping_sample_directory, str(sample_name) + '.bam')
    sorted_bam = os.path.join(read_mapping_sample_directory, str(sample_name) + '_sorted.bam')
    output_coverm = os.path.join(read_mapping_sample_directory, os.path.basename(sorted_bam).replace('sorted.bam', 'CoverM.tsv'))

    if os.path.exists(sorted_bam) and os.path.exists(output_coverm) and not args['force_read_mapping']:
        print(f"\033[1m{step_counter.print_sub_step()}: Skipping read mapping for {sample_name}, sorted BAM and coverM files already exist, and --force_read_mapping not provided...\033[0m")
    else:
        print(f"\033[1m{step_counter.print_sub_step()}: Starting the read mapping of {sample_name}...\033[0m")

        # If args.read_type is "short" or not provided, use Bowtie2 command
        if args['read_type'] == 'short' or not args['read_type']:
            # Check if "R1" is in the input_fastq filename
            if "R1" in input_fastq:
                # Create the corresponding R2 input filename
                input_fastq_r2 = input_fastq[:input_fastq.rfind("R1")] + "R2" + input_fastq[input_fastq.rfind("R1")+2:]
                # Check if the R2 input file exists
                if os.path.exists(input_fastq_r2) and not os.path.exists(output_sam):
                    print(f"\n\033[1m{step_counter.print_sub_step()}: Running Bowtie2: use paired fastq files as input against database created in the previous step to create SAM files...\033[0m")
                    subprocess.run(['bowtie2', '-x', reference_path, '-1', input_fastq, '-2', input_fastq_r2, '-S', output_sam, '-p', str(args['threads']), '--no-unal'])
                else:
                    print(f"\n\033[1m{step_counter.print_sub_step()}: Skipping mapping for {sample_name}, R2 input file '{input_fastq_r2}' not found...\033[0m")
            else:
                if os.path.exists(output_sam):
                    print(f"\n\033[1m{step_counter.print_sub_step()}:: Skipping Bowtie2: for {sample_name}, output SAM file already exists...\033[0m")
                else:
                    print(f"\n\033[1m{step_counter.print_sub_step()}: Running Bowtie2: use fastq file as input against the database created in the last step to create SAM files...\033[0m")
                    if args['interleaved'].upper() == 'FALSE':
                        subprocess.run(['bowtie2', '-x', reference_path, '-U', input_fastq, '-S', output_sam, '-p', str(args['threads']), '--no-unal'])
                    else:
                        subprocess.run(['bowtie2', '-x', reference_path, '--interleaved', input_fastq, '-S', output_sam, '-p', str(args['threads']), '--no-unal'])
        
        # If args.read_type is "long", use minimap2 command
        elif args['read_type'] == 'long':
            if os.path.exists(output_sam):
                print(f"\n\033[1m{step_counter.print_sub_step()}: Skipping minimap2: for {sample_name}, output SAM file already exists...\033[0m")
            else:
                print(f"\n\033[1m{step_counter.print_sub_step()}: Running Minimap2: use fastq file as input against database created in last step to create SAM files...\033[0m")
                subprocess.run(['minimap2', '-a', reference_path, input_fastq, '--sam-hit-only', '-t', str(args['threads']), '>', output_sam])

        if os.path.exists(output_bam):
            print(f"\n\033[1m{step_counter.print_sub_step()}: Skipping to convert SAM file to BAM for {sample_name}, output BAM file already exists...\033[0m")
        else:
            print(f"\n\033[1m{step_counter.print_sub_step()}: Running samtool view to convert SAM files to BAM...\033[0m")
            subprocess.run(['samtools', 'view', '-S', '-b', output_sam, '-o', output_bam, '-@', str(args['threads'])])
                
        print(f"\n\033[1m{step_counter.print_sub_step()}: Running samtool sort to sort BAM files...\033[0m")
        subprocess.run(['samtools', 'sort', output_bam, '-o', sorted_bam, '-@', str(args['threads'])])

        print(f"\n\033[1m{step_counter.print_sub_step()}: Running CoverM: use sorted BAM files to calculate read coverage and relative abundance of representative viral sequences...\033[0m")
        subprocess.run(['coverm', 'contig', '-b', sorted_bam, '-m', 'mean', 'trimmed_mean', 'covered_bases', 'covered_fraction', 'variance', 'length', 'count', 'reads_per_base', 'rpkm', 'tpm', '-o', output_coverm, '--output-format', 'sparse'])
        
        # Read in the CoverM output file as a DataFrame
        df = pd.read_csv(output_coverm, sep='\t')
        # Replace '_sorted' with an empty string in the 'Sample' column
        df['Sample'] = df['Sample'].str.replace('_sorted', '')
        # Write the modified DataFrame back to the output file
        df.to_csv(output_coverm, sep='\t', index=False)

    return read_mapping_sample_directory

def delete_files(read_mapping_sample_directory):
    print(f"\n\033[1m{step_counter.print_main_step()}: Removing tempory files...\033[0m")
    allowed_extensions = ('.bt2', '_sorted.bam', '.tsv')
    for file in os.listdir(read_mapping_sample_directory):
        if not file.endswith(allowed_extensions):
            os.remove(os.path.join(read_mapping_sample_directory, file))

def generate_summary_report(read_mapping_sample_directory, sample_name, formatted_start_time, formatted_end_time, duration, args):
    print(f"\n\033[1m{step_counter.print_main_step()}: Creating the summary report for Module 04 (Read mapping)...\033[0m")

    # Define the additional lines you want to add to the summary report
    module_04_header = """****************************************************************************
******************               MODULE 04                ******************
****************************************************************************
"""

    # Create a dictionary to hold argument descriptions and their default values
    argument_defaults = {
        '--input': args['input'],
        '--metadata': args['metadata'],
        '--sample-group': args['sample_group'],
        '--delete_files': args['delete_files'],
        '--threads': args['threads']}

    # Write a summary line with script arguments and their default values
    summary_line = "04_do_read_mapping.py"
    for arg, default in argument_defaults.items():
        if default is not None:
            summary_line += f" {arg} {default}"

    # Specify the path for the new MVP_Summary_Report.txt in '01_GENOMAD' directory
    summary_report_path_module_04 = os.path.join(read_mapping_sample_directory, str(sample_name) + '_MVP_04_Summary_Report.txt')

    # Write the combined content to the new summary report for Module 02
    with open(summary_report_path_module_04, 'w') as module_04_summary_report:
        module_04_summary_report.write(module_04_header + summary_line)
        module_04_summary_report.write(f"\n")
        module_04_summary_report.write(f"\nStart Time: {formatted_start_time}\n")
        module_04_summary_report.write(f"End time: {formatted_end_time}\n")
        module_04_summary_report.write(f"Running Time: {duration.total_seconds():.2f} seconds\n")

def main(args):
    # Capture start time
    mvp_start_time = datetime.datetime.now()
    mvp_formatted_start_time = mvp_start_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nStart Time: {mvp_formatted_start_time}") 

    # read metadata file and map FASTQ files
    metadata = pd.read_csv(args["metadata"], sep='\t')

    # Process rows based on specific sample numbers or all rows
    specific_sample_numbers = []
    if args['sample_group']:
        specific_sample_numbers = [int(num) for num in args['sample_group'].split(',') if num.strip()]

    for row_index, (_, row) in enumerate(metadata.iterrows(), start=1):
        sample_number = row['Sample_number']
        sample_name = row['Sample']
        input_fastq = row['Read_Path']

        # Check if the current sample number is in the list of specific sample numbers
        if specific_sample_numbers and sample_number not in specific_sample_numbers:
            continue # Skip to the next iteration

        step_counter.reset()

        # Capture start time
        start_time = datetime.datetime.now()
        formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\nStart Time of processing {sample_name}: {formatted_start_time}") 

        read_mapping_sample_directory = read_mapping(args, sample_name, input_fastq, row)

        # delete unwanted files
        if args['delete_files']:
            delete_files(read_mapping_sample_directory)

        # Capture end time
        end_time = datetime.datetime.now()
        formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

        # Calculate duration
        duration = end_time - start_time

        generate_summary_report(read_mapping_sample_directory, sample_name, formatted_start_time, formatted_end_time, duration, args)

    # Capture end time
    mvp_end_time = datetime.datetime.now()
    mvp_formatted_end_time = mvp_end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate duration
    mvp_duration = mvp_end_time - mvp_start_time

    message1 = "\033[1mModule 04 finished: read mapping executed successfully!\033[0m\n"
    message2 = f"Output files (sorted.bam and coverage output files) saved in the {args['input']}04_READ_MAPPING directories.\n"
    message3 = f"SAM and BAM files deleted if --delete_files used."
    message4 = f"Generated coverM.tsv files will be used as inputs for Module 05 (creation of vOTU tables)."
    message5 = "\n\033[1mYou can now proceed to the next step of the MVP script: Module 05!\033[0m"
    line_of_stars = '*' * len(message2)
    print()
    print(line_of_stars)
    print(message1)
    print(f"Start Time: {mvp_formatted_start_time}") 
    print(f"End Time: {mvp_formatted_end_time}")
    print(f"Running Time: {mvp_duration.total_seconds():.2f} seconds\n")
    print(message2)
    print(message3)
    print(message4)
    print(message5)
    print(line_of_stars)
    print()

    print("Please don't forget to cite MVP and the following softwares used by this module:")
    print("- Langmead B, Salzberg S. Fast gapped-read alignment with Bowtie 2. Nature Methods. 2012, 9:357-359\n")
    print("- Li, H., B. Handsaker, A. Wysoker, T. Fennell, J. Ruan, N. Homer, G. Marth, G. Abecasis, R. Durbin, and 1000 Genome Project Data Processing Subgroup. The Sequence Alignment/Map Format and SAMtools. Bioinformatics 25, no. 16 2009: 2078–79.\n")
    print("- Li H. New strategies to improve minimap2 alignment accuracy. Bioinformatics. 2021, 37(23):4572–4574. https://academic.oup.com/bioinformatics/article/37/23/4572/6384570?login=true\n")
    print("- https://github.com/wwood/CoverM\n")