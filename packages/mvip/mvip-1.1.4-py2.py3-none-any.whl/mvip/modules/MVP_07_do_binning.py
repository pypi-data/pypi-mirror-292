import os
import subprocess
import pandas as pd
import argparse
import shutil
import glob
import re
import taxopy
from Bio import SeqIO
from functools import reduce
import datetime
import time
import mvip

def fetch_arguments(parser):
    parser.set_defaults(func=main)
    parser.set_defaults(program="MVP_07_do_binning")
    parser.add_argument(
        "--input", "-i",
        help="Path to your working directory where you want to run MVP.",
    )
    parser.add_argument(
        "--metadata", "-m",
        help="Path to your metadata that you want to use to run MVP.",
    )
    parser.add_argument('--binning_sample_group', help='Specific sample number(s) to run the script on. You can provide a comma-separated list (1,2,3,4) or a range (1:4).', type=str, default='')
    parser.add_argument('--read_mapping_sample_group', help='Specific sample number(s) to run the script on. You can provide a comma-separated list (1,2,3,4) or a range (1:4).', type=str, default='')
    parser.add_argument('--keep_bam', action='store_true', help='Flag to indicate whether to keep BAM files', default=True)
    parser.add_argument('--force_vrhyme', action='store_true', help='Force execution of all steps, even if final_annotation_output_file exists.')
    parser.add_argument('--force_checkv', action='store_true', help='Force execution of all steps, even if final_annotation_output_file exists.')
    parser.add_argument('--checkv_db_path', help='Path to the CheckV database directory.', default='')
    parser.add_argument('--force_read_mapping', action='store_true', help='Force execution of all steps, even if final_annotation_output_file exists.')
    parser.add_argument('--read_type', type=str, default='short', choices=['short', 'long'], help='Sequencing data type (e.g. short vs long reads). Default = short')
    parser.add_argument('--interleaved', type=str, default='TRUE', help='Enable or disable the --interleaved option in Bowtie2 command (TRUE/FALSE)')
    parser.add_argument('--delete_files', action='store_true', help='flag to delete unwanted files')
    parser.add_argument('--normalization', type=str, default='RPKM', choices=['RPKM', 'FPKM'], help='Metrics to normalize')
    parser.add_argument('--force_outputs', action='store_true', help='Force execution of all steps, even if final_annotation_output_file exists.')
    parser.add_argument('--filtration', type=str, default='conservative', choices=['relaxed', 'conservative'], help='Filtration level ("relaxed" or "conservative"). Default = conservative')
    parser.add_argument('--viral_min_genes', dest='viral_min_genes', metavar='VIRAL_MIN_GENES', type=int, default=0, help='the minimum number of viral genes required to include a virus prediction (default = 0)')
    parser.add_argument('--host_viral_genes_ratio', dest='host_viral_genes_ratio', metavar='HOST_VIRAL_GENES_RATIO', type=float, default=1.0, help='the maximum ratio of host genes to viral genes required to include a virus prediction (default = 1)')
    parser.add_argument('--threads', type=int, default=1, help='Number of threads to use (default = 1)')

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

# Function to extract the list of sample numbers based on the provided input
def extract_sample_numbers(sample_group):
    if ',' in sample_group:
        # Split by comma and convert to integers
        sample_numbers = [int(s) for s in sample_group.split(',')]
    elif ':' in sample_group:
        # Extract the range and convert to integers
        start, end = [int(s) for s in sample_group.split(':')]
        sample_numbers = list(range(start, end + 1))
    else:
        # If no comma or colon, consider the input as a single number
        sample_numbers = [int(sample_group)]
    return sample_numbers

def set_up_paths(args):
    # read metadata file and map FASTQ files
    metadata_df = pd.read_csv(args['metadata'], delimiter='\t')

    # Filter the DataFrame based on the --sample-group flag
    if args['binning_sample_group']:
        sample_numbers = extract_sample_numbers(args['binning_sample_group'])
        filtered_metadata_df = metadata_df[metadata_df['Sample_number'].isin(sample_numbers)]
    else:
        filtered_metadata_df = metadata_df

    # Create the output folder if it doesn't exist
    output_folder = os.path.join(args['input'], '07_BINNING')
    os.makedirs(output_folder, exist_ok=True)

    # Correctly construct the 'fasta' file path
    fasta = os.path.join(args['input'], '03_CLUSTERING', 'MVP_03_All_Sample_Filtered_Relaxed_Representative_Virus_Provirus_Sequences.fna')

    # Get the list of BAM file paths from the filtered metadata
    bam_file_paths = [os.path.join(args['input'], '04_READ_MAPPING', str(row['Sample']), f'{row["Sample"]}_sorted.bam')
        for index, row in filtered_metadata_df.iterrows()]

    # Get the list of BAM files in the 07_BINNING directory with the _sorted.bam pattern
    output_folder_path = os.path.join(output_folder, '07A_vRHYME_OUTPUT')

    return filtered_metadata_df, output_folder, fasta, bam_file_paths, output_folder_path

def binning_step(args, output_folder_path, fasta, bam_file_paths):
    if not args['force_vrhyme'] and os.path.exists(output_folder_path):
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping binning using vRhyme because {output_folder_path} already exists and --force_vrhyme not provided...\033[0m")
    else:
        print(f"\n\033[1m{step_counter.print_main_step()}: Running binning using vRhyme...\033[0m")
        if os.path.exists(output_folder_path):
            shutil.rmtree(output_folder_path)
            if args['keep_bam']:
                vRhyme_command = ['vRhyme', '-i', fasta, '-b', *bam_file_paths,  '-o', output_folder_path , '--keep_bam', '--verbose', '-t', str(args['threads'])]
            else:
                vRhyme_command = ['vRhyme', '-i', fasta, '-b', *bam_file_paths,  '-o', output_folder_path, '--verbose', '-t', str(args['threads'])]
        else:
            if args['keep_bam']:
                vRhyme_command = ['vRhyme', '-i', fasta, '-b', *bam_file_paths,  '-o', output_folder_path , '--keep_bam', '--verbose', '-t', str(args['threads'])]
            else:
                vRhyme_command = ['vRhyme', '-i', fasta, '-b', *bam_file_paths,  '-o', output_folder_path, '--verbose', '-t', str(args['threads'])]

        # Execute the vRhyme command
        subprocess.run(vRhyme_command)

        # Remove BAM.bai files at the end of the script
        for bam_file in bam_file_paths:
            bai_file_path = os.path.join(bam_file + '.bai')
            if os.path.exists(bai_file_path):
                os.remove(bai_file_path)

    # Read the vRhyme outputs into pandas DataFrames
    vRhyme_output_files = glob.glob(os.path.join(output_folder_path, '*.tsv'))

    return vRhyme_output_files

def empty_binning_summary_report(args, start_time, output_folder_path):
    print(f"\033[1m{step_counter.print_main_step()}: No bin generated by vRhyme. Skipping the next steps and generating the summary report...\033[0m")

    # Capture end time
    formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.now()
    formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate duration
    duration = end_time - start_time
    
    # Define the path for the new summary report for Module 03
    summary_report_path_module_07 = os.path.join(args['input'], '07_BINNING', 'MVP_07_Summary_Report.txt')

    # Create a dictionary to hold argument descriptions and their default values
    argument_defaults = {
        '--input': args['input'],
        '--metadata': args['metadata'],
        '--binning_sample_group': args['binning_sample_group'],
        '--read_mapping_sample_group': args['read_mapping_sample_group'],
        '--keep_bam': args['keep_bam'],
        '--force_vrhyme': args['force_vrhyme'],
        '--threads': args['threads']}
    
    # Write a summary line with script arguments and their default values
    summary_line = "07_do_binning.py"
    for arg, default in argument_defaults.items():
        if default is not None:
            summary_line += f" {arg} {default}"

    start_time = f"\nStart Time: {formatted_start_time}"
    end_time = f"End time: {formatted_end_time}"
    duration = f"Running Time: {duration.total_seconds():.2f} seconds\n"

    # Prepare the content for Module 03 summary report
    module_07_header = f"""****************************************************************************
    ******************               MODULE 07                ******************
    ****************************************************************************

    {summary_line}
    {start_time}
    {end_time}
    {duration}

    Summary Report before filtration
    --------------------------
    vBins generated:     0
    Binned sequences:   0 (0%)

    See the log file to more details
    """

    with open(summary_report_path_module_07, 'w') as module_07_summary_report:
        module_07_summary_report.write(module_07_header)

    message1 = "\033[1mModule 07 finished: vRhyme executed successfully!\033[0m\n"
    message2 = f"vRhyme outputs have been generated in {output_folder_path}.\n"
    message3 = f"Summary report for Module 07 has been created: {summary_report_path_module_07})."
    line_of_stars = '*' * len(message3)
    print()
    print(line_of_stars)
    print(message1)
    print(f"Start Time: {formatted_start_time}") 
    print(f"End Time: {formatted_end_time}")
    print(f"Running Time: {duration}")
    print(message2)
    print(message3)
    print(line_of_stars)
    print()
    print("Please don't forget to cite MVP the following softwares used by this module:")
    print("- Kieft, K., Adams, A., Salamzade, R., Kalan, L., & Anantharaman, K. vRhyme enables binning of viral genomes from metagenomes. Nucleic Acids Research, 2022.\n")

def checkv(args, output_folder, output_folder_path):
    # Create directory for CheckV analysys of vBins
    checkv_vBins_directory_path = os.path.join(output_folder, '07B_vBINS_CHECKV')
    os.makedirs(checkv_vBins_directory_path, exist_ok=True)
    checkv_output_directory_path = os.path.join(checkv_vBins_directory_path, 'CHECKV_VBINS_OUTPUT')
    checkv_input_genome_vBins_fasta_file_path = os.path.join(checkv_vBins_directory_path, 'All_Genome_Fasta_vBins_CheckV_Input.fasta')

    # Determine the checkV database path
    checkv_db_path = os.path.join(args['input'], '02_CHECK_V', 'checkv-db-v1.5')
    if args['checkv_db_path']:
        checkv_db_path = args['checkv_db_path']

    if os.path.exists(checkv_output_directory_path) and not args['force_checkv']:
        print(f"\033[1m{step_counter.print_main_step()}: Skipping running CheckV, {checkv_output_directory_path} already exists and --force_checkv not provided...\033[0m")
    else:
        print(f"\033[1m{step_counter.print_main_step()}: Running CheckV on vRhyme binning outputs...\033[0m")
        with open(checkv_input_genome_vBins_fasta_file_path, 'w') as checkv_input_genome_vBins_fasta_file:
            for filename in os.listdir(os.path.join(output_folder_path, 'vRhyme_best_bins_fasta')):
                if filename.endswith('.fasta'):
                    input_fasta_filepath = os.path.join(output_folder_path, 'vRhyme_best_bins_fasta', filename)
                    first_sequence = True
                    merged_sequence = ""
                    with open(input_fasta_filepath, 'r') as input_file:
                        for record in SeqIO.parse(input_file, 'fasta'):
                        # Keep only the header of the first sequence
                            if first_sequence:
                                new_header = f'>vBin_{record.id.split("_")[1]}'
                                first_sequence = False
                            # Merge all sequences
                            merged_sequence += str(record.seq) + 'N' * 10

                        # Write the modified record to the output file
                        checkv_input_genome_vBins_fasta_file.write(f'{new_header}\n{merged_sequence.rstrip("N")}\n')

        # Run CheckV
        subprocess.run(['checkv', 'end_to_end', checkv_input_genome_vBins_fasta_file_path, checkv_output_directory_path, '-d', checkv_db_path, '-t', str(args['threads']), '--remove_tmp'])

    return checkv_output_directory_path, checkv_input_genome_vBins_fasta_file_path


def generate_index(args, output_folder):
    # Create directory for read mapping of vBins
    read_mapping_vBins_directory = os.path.join(output_folder, '07C_vBINS_READ_MAPPING')
    reference_path = os.path.join(read_mapping_vBins_directory, 'reference_vBins')

    os.makedirs(read_mapping_vBins_directory, exist_ok=True)

    vBins_fasta_files = []
    vBins_fasta_files_pattern = os.path.join(output_folder, '07A_vRHYME_OUTPUT', 'vRhyme_best_bins_fasta', '*.fasta')
    vBins_fasta_files.extend(glob.glob(vBins_fasta_files_pattern, recursive=True))

    if args['read_type'] == 'short' or not args['read_type']:
        if os.path.exists(reference_path + '.1.bt2') and not args['force_read_mapping']:
            print(f"\n\033[1m{step_counter.print_main_step()}: Skipping running Bowtie-2-build because reference index {reference_path} already exists in {read_mapping_vBins_directory}, and --force_read_mapping not provided...\033[0m")
        else:
            print(f"\n\033[1m{step_counter.print_main_step()}: Run bowtie2-build: use representative viral sequences to build bowtie database...\033[0m")
            subprocess.run(['bowtie2-build', *vBins_fasta_files, reference_path])
    else:
        # If args.read_type is "long," apply minimap2 to create an index (assuming minimap2 is in your PATH)
        if os.path.exists(reference_path + '.mmi') and not args['force_read_mapping']:
            print(f"\n\033[1m{step_counter.print_main_step()}: Skipping running minimap2 because reference index {reference_path} already exists in {read_mapping_vBins_directory}, and --force_read_mapping not provided...\033[0m")
        else:
            print(f"\n\033[1m{step_counter.print_main_step()}: Run minimap2 to create an index from representative viral sequences...\033[0m")
            subprocess.run(['minimap2', '-d', reference_path, *vBins_fasta_files])

    return read_mapping_vBins_directory, reference_path, vBins_fasta_files

def read_mapping(args, output_folder, filtered_metadata_df, read_mapping_vBins_directory, reference_path, vBins_fasta_files):
    coverM_vBins_output_file_path = os.path.join(read_mapping_vBins_directory, f"MVP_07_Unfiltered_best_vBins_read_mapping_information_{args['normalization']}_Table.tsv")

    if not os.path.exists(coverM_vBins_output_file_path) or args['force_read_mapping']:
        vBins_fasta_files_folder = os.path.join(output_folder, '07A_vRHYME_OUTPUT', 'vRhyme_best_bins_fasta')
        
        # Process rows based on specific sample numbers or all rows
        specific_sample_numbers = []
        if args['read_mapping_sample_group']:
            specific_sample_numbers = [int(num) for num in args['read_mapping_sample_group'].split(',') if num.strip()]

        for row_index, (_, row) in enumerate(filtered_metadata_df.iterrows(), start=1):
            sample_number = row['Sample_number']
            sample_name = row['Sample']

            # Check if the current sample number is in the list of specific sample numbers
            if specific_sample_numbers and sample_number not in specific_sample_numbers:
                continue # Skip to the next iteration

            # Create directories for the current sample in 07C_vBINS_READ_MAPPING
            read_mapping_sample_directory = os.path.join(read_mapping_vBins_directory, str(sample_name))
            os.makedirs(read_mapping_sample_directory, exist_ok=True)

            input_fastq = row['Read_Path']
            sample_name = row['Sample']
            output_sam = os.path.join(read_mapping_sample_directory, str(sample_name) + '.sam')
            output_bam = os.path.join(read_mapping_sample_directory, str(sample_name) + '.bam')
            sorted_bam = os.path.join(read_mapping_sample_directory, str(sample_name) + '_sorted.bam')
            output_coverm = os.path.join(read_mapping_sample_directory, os.path.basename(sorted_bam).replace('sorted.bam', 'vBins_CoverM.tsv'))

            print(f"\n\033[1m{step_counter.print_sub_step()}: Starting the read mapping of {sample_name}...\033[0m")
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
                        print(f"\n\033[1m{step_counter.print_sub_step()}: Skipping mapping for {sample_name}, R2 input file {input_fastq_r2} not found...\033[0m")
                else:
                    if os.path.exists(output_sam):
                        print(f"\n\033[1m{step_counter.print_sub_step()}: Skipping Bowtie2: for {sample_name}, output SAM file already exists...\033[0m")
                    else:
                        print(f"\n\033[1m{step_counter.print_sub_step()}: Running Bowtie2: use fastq file as input against the database created in the last step to create SAM files...\033[0m")
                        if args['interleaved'].upper() == 'FALSE':
                            subprocess.run(['bowtie2', '-x', reference_path, '-U', input_fastq, '-S', output_sam, '-p', str(args['threads']), '--no-unal'])
                        else:
                            subprocess.run(['bowtie2', '-x', reference_path, '--interleaved', input_fastq, '-S', output_sam, '-p', str(args['threads']), '--no-unal'])
            
            # If args.read_type is "long", use minimap2 command
            elif args['read_type'] == 'long':
                if os.path.exists(output_sam):
                    print(f"\n\033[1m{step_counter.print_sub_step()}: Skipping Bowtie2: for {sample_name}, output SAM file already exists...\033[0m")
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
            subprocess.run(['coverm', 'genome', '-b', sorted_bam, '-d', vBins_fasta_files_folder, '-x', 'fasta', '-m', 'mean', 'trimmed_mean', 'covered_bases', 'covered_fraction', 'variance', 'rpkm', 'tpm', '-o', output_coverm, '--output-format', 'sparse'])

            # Read in the CoverM output file as a DataFrame
            df = pd.read_csv(output_coverm, sep='\t')

            if df.shape[0] == 0:
                # If df is empty, create a new DataFrame for artificial lines
                artificial_lines_data = []

                for vBin_file in vBins_fasta_files:
                    print(f"Adding line for {vBin_file}:")
                    vBin_id = os.path.splitext(os.path.basename(vBin_file))[0]

                    new_row = {'Sample': sample_name, 'Genome': vBin_id}
                    # Set all other columns to 0
                    for col in df.columns.difference(['Sample', 'Genome']):
                        new_row[col] = 0

                    # Append the new row to the list
                    artificial_lines_data.append(new_row)

                # If there are rows in the list, concatenate them to the artificial lines DataFrame
                if artificial_lines_data:
                    artificial_lines = pd.DataFrame(artificial_lines_data, columns=df.columns)
                    # Concatenate the artificial lines DataFrame with the original DataFrame
                    df = pd.concat([df, artificial_lines], ignore_index=True)
                df.to_csv(output_coverm, index=False)
            else:
                # Replace '_sorted' with an empty string in the 'Sample' column
                df['Sample'] = df['Sample'].str.replace('_sorted', '')
                # Write the modified DataFrame back to the output file
                df.to_csv(output_coverm, index=False)
            
            # delete unwanted files
            print(f"\n\033[1m{step_counter.print_main_step()}: Deleting temporary files...\033[0m")
            if args['delete_files']:
                allowed_extensions = ('.bt2', '_sorted.bam', '.tsv')
                for file in os.listdir(read_mapping_sample_directory):
                    if not file.endswith(allowed_extensions):
                        os.remove(os.path.join(read_mapping_sample_directory, file))

            # Combine all CoverM CSV files into one
            print(f"\n\033[1m{step_counter.print_main_step()}: Merging all coverM output tables...\033[0m")
            coverm_file_path_dir = os.path.join(read_mapping_vBins_directory, '*', '*_CoverM.tsv')
            all_coverm_files = glob.glob(coverm_file_path_dir, recursive=True)
            dfs = []

            for filename in all_coverm_files:
                df = pd.read_csv(filename, usecols=['Sample', 'Genome', 'Covered Fraction', args['normalization']]).drop_duplicates(subset=['Sample', 'Genome'], keep='last').pivot(index=['Genome'], columns='Sample')
                df.columns = ['_'.join(str(col) for col in cols).strip() for cols in df.columns.values]
                dfs.append(df)

            coverM_vBins_output_file_df = reduce(lambda left, right: pd.merge(left, right, on=['Genome'], how='outer'), dfs).reset_index()
            coverM_vBins_output_file_df['Genome'] = coverM_vBins_output_file_df['Genome'].replace({'vRhyme_bin': 'vBin'}, regex=True)
            coverM_vBins_output_file_df.to_csv(coverM_vBins_output_file_path, sep='\t', index=False)
    else:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping read mapping, {coverM_vBins_output_file_path} file already exists, and --force_read_mapping not provided...\033[0m")
        coverM_vBins_output_file_df = pd.read_csv(coverM_vBins_output_file_path, sep='\t')
    
    return coverM_vBins_output_file_df


def merge_tables(args, output_folder_path, vRhyme_output_files, read_mapping_vBins_directory, checkv_output_directory_path, coverM_vBins_output_file_df):
    contig_summary_vRhyme_merged_path = os.path.join(output_folder_path, f'MVP_07_Merged_vRhyme_Outputs_Unfiltered_best_vBins_Memberships_Table.tsv')
    if os.path.exists(contig_summary_vRhyme_merged_path) and not args['force_outputs']:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping generating {contig_summary_vRhyme_merged_path}, file already exists, and --force_outputs not provided...\033[0m")
        contig_summary_vRhyme_merged_df = pd.read_csv(contig_summary_vRhyme_merged_path, sep='\t')
    else:
        print(f"\n\033[1m{step_counter.print_main_step()}: Generating {contig_summary_vRhyme_merged_path}...\033[0m")
        summary_df = pd.read_csv(next(file for file in vRhyme_output_files if '.summary.tsv' in file), sep='\t')
        summary_df = summary_df.rename(columns={'bin': 'virus_id'})
        summary_df['virus_id'] = summary_df['virus_id'].astype(str)

        membership_df = pd.read_csv(next(file for file in vRhyme_output_files if 'membership.tsv' in file), sep='\t') 
        membership_df = membership_df.rename(columns={'bin': 'virus_id', 'scaffold': 'vBins_membership'})
        membership_df['virus_id'] = membership_df['virus_id'].astype(str)

        vRhyme_merged_df = pd.merge(summary_df, membership_df, on='virus_id', how='left')
        vRhyme_merged_df['virus_id'] = vRhyme_merged_df['virus_id'].apply(lambda x: f'vBin_{x}')
        vRhyme_merged_df = vRhyme_merged_df.add_prefix('vBins_')
        vRhyme_merged_df = vRhyme_merged_df.rename(columns={'vBins_virus_id': 'virus_id', 'vBins_vBins_membership': 'vBins_membership'})

        contig_summary_file_path = os.path.join(args['input'], '03_CLUSTERING', 'MVP_03_All_Sample_Filtered_Relaxed_Merged_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv')
        contig_summary_file_df = pd.read_csv(contig_summary_file_path, sep='\t', usecols=['virus_id', 'provirus', 'taxonomy', 'Genome type', 'Host type'])
        contig_summary_file_df = contig_summary_file_df.add_prefix('membership_')
        contig_summary_file_df = contig_summary_file_df.rename(columns={'membership_virus_id': 'vBins_membership'})
        contig_summary_vRhyme_merged_df = pd.merge(vRhyme_merged_df, contig_summary_file_df, on='vBins_membership', how='left')
        contig_summary_vRhyme_merged_df.to_csv(contig_summary_vRhyme_merged_path, sep='\t', index=False)

    unfiltered_output_read_mapping_file_path = os.path.join(read_mapping_vBins_directory, f"MVP_07_Merged_vRhyme_Outputs_Unfiltered_best_vBins_Memberships_geNomad_CheckV_Summary_read_mapping_information_{args['normalization']}_Table.tsv")
    if os.path.exists(unfiltered_output_read_mapping_file_path) and not args['force_outputs']:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping generating {unfiltered_output_read_mapping_file_path}, file already exists, and not force argument provided...\033[0m")
        unfiltered_output_read_mapping_file_df = pd.read_csv(unfiltered_output_read_mapping_file_path, sep='\t')
    else:
        print(f"\n\033[1m{step_counter.print_main_step()}: Generating {unfiltered_output_read_mapping_file_path}...\033[0m")
        checkV_vBins_summary_file_path = os.path.join(checkv_output_directory_path, 'quality_summary.tsv')
        checkV_vBins_summary_file_df = pd.read_csv(checkV_vBins_summary_file_path, sep='\t')
        checkV_vBins_summary_file_df = checkV_vBins_summary_file_df.rename(columns={'contig_id': 'virus_id', 'contig_length': 'vBins_length', 'warnings': 'vBins_warnings'})
        columns_to_remove = ['provirus', 'proviral_length', 'contamination']
        checkV_vBins_summary_file_df.drop(columns=columns_to_remove, inplace=True)
        checkV_contig_summary_vRhyme_merged_df = pd.merge(contig_summary_vRhyme_merged_df, checkV_vBins_summary_file_df, on='virus_id', how='left')
        unfiltered_output_read_mapping_file_df = pd.merge(checkV_contig_summary_vRhyme_merged_df, coverM_vBins_output_file_df, left_on='virus_id', right_on='Genome', how='left').drop('Genome', axis=1)

        # Assuming 'Unfiltered_vRhyme_best_bins_circular_genomad_checkV_information.tsv' is the desired output file name
        unfiltered_output_read_mapping_file_df.to_csv(unfiltered_output_read_mapping_file_path, sep='\t', index=False)

    return contig_summary_vRhyme_merged_df, unfiltered_output_read_mapping_file_df

def filter_tables(args, output_folder, unfiltered_output_read_mapping_file_df):
    summary_report_path_module_05 = os.path.join(args['input'], '05_VOTU_TABLES', 'MVP_05_Summary_Report.txt')
    with open(summary_report_path_module_05, 'r') as module_05_summary_report:
        module_05_summary_content = module_05_summary_report.read()
    target_line = next((line for line in module_05_summary_content.split('\n') if line.startswith('05_create_votu_table.py')), None)
    vBins_vOTUs_table_Folder_path = os.path.join(output_folder, '07D_vBINS_vOTUS_TABLES')
    filtered_output_file_path = os.path.join(vBins_vOTUs_table_Folder_path, f"MVP_07_Merged_vRhyme_Outputs_Filtered_{args['filtration']}_best_vBins_geNomad_CheckV_Summary_read_mapping_information_{args['normalization']}_Table.tsv")
    
    if os.path.exists(filtered_output_file_path) and not args['force_outputs']:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping filtering {filtered_output_file_path}, file already exists, and --force_outputs not provided...\033[0m")
        filtered_output_file_df = pd.read_csv(filtered_output_file_path, sep='\t')
    else:
        if os.path.exists(vBins_vOTUs_table_Folder_path):
            shutil.rmtree(vBins_vOTUs_table_Folder_path)
            os.makedirs(vBins_vOTUs_table_Folder_path)
        else:
            os.makedirs(vBins_vOTUs_table_Folder_path, exist_ok=True)

        if os.path.exists(filtered_output_file_path):
            print(f"\n\033[1m{step_counter.print_main_step()}: Skipping filtering {filtered_output_file_path}, file already exists, and --force_outputs not provided...\033[0m")
            filtered_output_file_df = pd.read_csv(filtered_output_file_path, sep='\t')
        else:
            # Apply the new filtration logic if args.filtration is conservative
            if args['filtration'] == 'conservative':
                print(f"\n\033[1m{step_counter.print_sub_step()}: Filtering (vRhyme conservative mode) {filtered_output_file_path}...\033[0m")
                filtered_output_file_df = unfiltered_output_read_mapping_file_df[unfiltered_output_read_mapping_file_df['vBins_redundancy'] < 2]
            else: 
                print(f"\n\033[1m{step_counter.print_sub_step()}: Filtering (vRhyme relaxed mode) {filtered_output_file_path}...\033[0m")
                filtered_output_file_df = unfiltered_output_read_mapping_file_df[unfiltered_output_read_mapping_file_df['vBins_redundancy'] < 6]

            # Define the filtration argument used in Module 05
            filtration_option = re.search(r'--filtration (\w+)', target_line).group(1) if target_line else None

            # Apply relaxed filtration criteria
            print(f"\n\033[1m{step_counter.print_sub_step()}: Filtering (MVP relaxed mode) {filtered_output_file_path}...\033[0m")
            filtered_output_file_df = filtered_output_file_df.loc[(filtered_output_file_df['viral_genes'] >= args['viral_min_genes'])]
            filtered_output_file_df = filtered_output_file_df.loc[filtered_output_file_df['host_genes']/filtered_output_file_df['viral_genes'] <= args['host_viral_genes_ratio']]

            # Apply the new filtration logic if args.filtration is conservative
            if filtration_option == 'conservative':
                print(f"\n\033[1m{step_counter.print_sub_step()}: Filtering (MVP conservative mode) {filtered_output_file_path}...\033[0m")
                filtered_output_file_df = filtered_output_file_df.loc[
                    (((filtered_output_file_df['completeness_method'].str.contains('AAI-based')) | (filtered_output_file_df['completeness_method'].str.contains('DTR'))) &
                    (filtered_output_file_df['checkv_quality'].isin(['High-quality', 'Medium-quality']))) | (filtered_output_file_df['vBins_length'] > 5000)]

            # Group by 'vBins_id' and aggregate 'vBins_membership' by joining with ';'
            # Columns to remove
            grouped_filtered_output_file_df = filtered_output_file_df.groupby('virus_id').agg({'vBins_membership': ';'.join, 'membership_provirus': ';'.join}).reset_index()
            columns_to_remove = ['vBins_membership', 'membership_provirus', 'membership_taxonomy', 'membership_Genome type', 'membership_Host type']
            filtered_output_file_df = filtered_output_file_df.drop(columns=columns_to_remove)
            filtered_output_file_df = pd.merge(grouped_filtered_output_file_df, filtered_output_file_df, on='virus_id', how='left')  

    return filtered_output_file_path, vBins_vOTUs_table_Folder_path, target_line, filtered_output_file_df

def empty_binning_after_filtration_summary_report(args, start_time, output_folder_path):
    print(f"\n\033[1m{step_counter.print_main_step()}: No remaining vBin generated by vRhyme after filtration. Skipping the next steps and generating the summary report...\033[0m")

    # Capture end time
    formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.now()
    formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate duration
    duration = end_time - start_time

    summary_report_path_module_07 = os.path.join(args['input'], '07_BINNING', 'MVP_07_Summary_Report.txt')

    # Create a dictionary to hold argument descriptions and their default values
    argument_defaults = {
        '--input': args['input'],
        '--metadata': args['metadata'],
        '--binning_sample_group': args['binning_sample_group'],
        '--read_mapping_sample_group': args['read_mapping_sample_group'],
        '--keep_bam': args['keep_bam'],
        '--force_vrhyme': args['force_vrhyme'],
        '--force_checkv': args['force_checkv'],
        '--force_read_mapping': args['force_read_mapping'],
        '--interleaved': args['interleaved'],
        '--delete_files': args['delete_files'],
        '--normalization': args['normalization'],
        '--force_outputs': args['force_outputs'],
        '--filtration': args['filtration'],
        '--viral_min_genes': args['viral_min_genes'],
        '--host_viral_genes_ratio': args['host_viral_genes_ratio'],
        '--threads': args['threads']}
    

    # Write a summary line with script arguments and their default values
    summary_line = "07_do_binning.py"
    for arg, default in argument_defaults.items():
        if default is not None:
            summary_line += f" {arg} {default}"

    start_time = f"\nStart Time: {formatted_start_time}"
    end_time = f"End time: {formatted_end_time}"
    duration = f"Running Time: {duration.total_seconds():.2f} seconds\n"

    # Prepare the content for Module 03 summary report
    module_07_summary_content = f"""****************************************************************************
******************               MODULE 07                ******************
****************************************************************************

{summary_line}
{start_time}
{end_time}
{duration}

Summary Report after filtration
--------------------------
vBins generated:     0
Binned sequences:   0 (0%)

See the log file to more details
"""

    # Write the content to the new summary report for Module 03
    with open(summary_report_path_module_07, 'w') as module_07_summary_report:
        module_07_summary_report.write(module_07_summary_content)

    print("Summary report for Module 07 has been created: ", summary_report_path_module_07)
    message1 = "\n\033[1mModule 07 finished: vRhyme executed successfully!\033[0m\n"
    message2 = f"vRhyme outputs have been generated in {output_folder_path}.\n"
    message3 = f"Summary report for Module 07 has been created: summary_report_path_module_07)"
    line_of_stars = '*' * len(message3)
    print()
    print(line_of_stars)
    print(message1)
    print(f"Start Time: {formatted_start_time}") 
    print(f"End Time: {formatted_end_time}")
    print(f"Running Time: {duration}")
    print(duration)
    print(message2)
    print(message3)
    print(line_of_stars)
    print()
    print("Please don't forget to cite the following softwares used by this module:")
    print("- Kieft, K., Adams, A., Salamzade, R., Kalan, L., & Anantharaman, K. vRhyme enables binning of viral genomes from metagenomes. Nucleic Acids Research, 2022.\n")


def generate_warning(row):
    existing_warnings = row['vBins_warnings'] if pd.notna(row['vBins_warnings']) else ''
    warnings = [existing_warnings]

    # Check condition 1
    if row['vBins_members'] >= 4:
        warnings.append('Most vBins are just 2-3 members and few exceed 4 members. Potential contamination')

    # Check condition 2
    if 'Yes' in row['membership_provirus']:
        warnings.append('Prophages are difficult to bin. Potential contamination')

    # Check condition 3
    if row['vBins_length'] > 500000:
        warnings.append('Potential contamination')

    # Join multiple warnings with '|'
    all_warnings = existing_warnings + '|' + '|'.join(warnings) if existing_warnings else '|'.join(warnings)
    return all_warnings


def find_taxonomy_consensus(unfiltered_output_read_mapping_file_df, filtered_output_file_df, filtered_output_file_path):
    print(f"\n\033[1m{step_counter.print_main_step()}: Finding consensus taxonomy...\033[0m")

    # download taxonomic information from NCBI's servers and put this data into a TaxDb object
    ncbi_taxdb = taxopy.TaxDb(keep_files=True)
    # Create a new column 'Tax_name' with only the last level of the 'membership_taxonomy' value
    unfiltered_output_read_mapping_file_df['Tax_name'] = unfiltered_output_read_mapping_file_df['membership_taxonomy'].apply(lambda x: x.split(';')[-1])
    # Create an empty column 'TaxID' to store the taxid values
    unfiltered_output_read_mapping_file_df['TaxID'] = None

    for index, row in unfiltered_output_read_mapping_file_df.iterrows():
        tax_name = row['Tax_name']
        taxid = taxopy.taxid_from_name(tax_name, ncbi_taxdb)
        taxid = str(taxid).strip('[]')
        # Update the 'taxname' column for the current row
        unfiltered_output_read_mapping_file_df.loc[index, 'TaxID'] = taxid if taxid else 1

    # Create a new DataFrame with only the 'virus_id', 'Tax_name', and 'TaxID' columns
    df_taxonomy = unfiltered_output_read_mapping_file_df[['virus_id','Tax_name', 'TaxID']]

    # Iterate over unique virus_id values
    for virus_id in df_taxonomy['virus_id'].unique():
        # Extract TaxID values for the current virus_id
        taxid_values = df_taxonomy.loc[df_taxonomy['virus_id'] == virus_id, 'TaxID'].tolist()

        # Create a list to store taxid_info for each TaxID value
        taxid_info_list = []
        
        # Iterate over each TaxID value
        for taxid_vBin in taxid_values:
            taxid_vBin = int(taxid_vBin)
            # Retrieve taxonomic information for the current TaxID
            taxid_info = taxopy.Taxon(taxid_vBin, ncbi_taxdb)
            # Append taxonomic information to the list
            taxid_info_list.append(taxid_info)
        
        # Run majority vote using taxid_info_list
        majority_vote = taxopy.find_majority_vote(taxid_info_list, ncbi_taxdb)
        # Update the 'Consensus_taxonomy' column for the current virus_id
        df_taxonomy.loc[df_taxonomy['virus_id'] == virus_id, 'Consensus_taxonomy_name'] = majority_vote.name

    # Keep only the 'virus_id' and 'Consensus_taxonomy' columns
    df_consensus_taxonomy = df_taxonomy[['virus_id', 'Consensus_taxonomy_name']]
    df_consensus_taxonomy['Consensus_taxonomy_name'] = df_consensus_taxonomy['Consensus_taxonomy_name'].replace('root', 'Unclassified')

    # Merge df_consensus_taxonomy and df_unfiltered_output
    unfiltered_output_read_mapping_file_df = unfiltered_output_read_mapping_file_df[['Tax_name', 'membership_taxonomy', 'membership_Genome type', 'membership_Host type']]
    unfiltered_output_read_mapping_file_df = unfiltered_output_read_mapping_file_df.drop_duplicates()

    merged_df = pd.merge(df_consensus_taxonomy, unfiltered_output_read_mapping_file_df, how='left', left_on='Consensus_taxonomy_name', right_on='Tax_name')
    merged_df['membership_taxonomy'].fillna(merged_df['Consensus_taxonomy_name'], inplace=True)

    # Replace blank values in 'membership_Genome type' and 'membership_Host type' with 'Unknown'
    merged_df['membership_Genome type'].fillna('Unknown', inplace=True)
    merged_df['membership_Host type'].fillna('Unknown', inplace=True)

    # Rename 'membership_taxonomy' column to 'Consensus_taxonomy'
    merged_df.rename(columns={'membership_taxonomy': 'Consensus_taxonomy'}, inplace=True)

    merged_df = merged_df.drop('Tax_name', axis=1)
    merged_df = merged_df.drop_duplicates()

    # Apply the custom function to create or update the 'vBins_warnings' column
    filtered_output_file_df['vBins_warnings'] = filtered_output_file_df.apply(generate_warning, axis=1)
    consensus_filtered_output_file_df = filtered_output_file_df.drop_duplicates()
    
    consensus_filtered_output_file_df = pd.merge(consensus_filtered_output_file_df, merged_df, how='left', on='virus_id')
    consensus_filtered_output_file_df.to_csv(filtered_output_file_path, sep='\t', index=False)

    return consensus_filtered_output_file_df
    

def combine_vBin_unbinned_tables(args, vBins_vOTUs_table_Folder_path, consensus_filtered_output_file_df, contig_summary_vRhyme_merged_df):
    binned_unbinned_filtered_output_file_path = os.path.join(vBins_vOTUs_table_Folder_path, f"MVP_07_Merged_vRhyme_Outputs_Filtered_{args['filtration']}_best_vBins_Representative_Unbinned_vOTUs_geNomad_CheckV_Summary_read_mapping_information_{args['normalization']}_Table.tsv")

    if os.path.exists(binned_unbinned_filtered_output_file_path) and not args['force_outputs']:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping generating {binned_unbinned_filtered_output_file_path}, file already exists, and --force_outputs not provided...\033[0m")
        binned_unbinned_filtered_output_file_df = pd.read_csv(binned_unbinned_filtered_output_file_path, sep='\t')
        return binned_unbinned_filtered_output_file_df
    else:
        print(f"\n\033[1m{step_counter.print_main_step()}: Creating merged vBin and unbinned output tables...\033[0m")
        consensus_filtered_output_file_df['Type'] = 'vBin'
        consensus_filtered_output_file_df = consensus_filtered_output_file_df.rename(columns={'Consensus_taxonomy': 'taxonomy', 'membership_Genome type': 'Genome type', 'membership_Host type': 'Host type', 'vBins_length': 'virus_length', 'membership_provirus': 'provirus'})
        unbinned_file_path = os.path.join(args['input'], '05_VOTU_TABLES', 'MVP_05_All_Sample_Filtered_conservative_Representative_Virus_Proviruses_vOTU_RPKM_Table.tsv')
        unbinned_file_df = pd.read_csv(unbinned_file_path, sep='\t')
        unbinned_file_df['Type'] = 'Unbinned_Contig'

        # Assuming 'virus_id' is the common column between the two DataFrames
        unbinned_list_df = pd.merge(unbinned_file_df, contig_summary_vRhyme_merged_df[['vBins_membership']], left_on='virus_id', right_on='vBins_membership', how='left', indicator=True)
        unbinned_list_df = unbinned_list_df[unbinned_list_df['_merge'] == 'left_only'].drop('_merge', axis=1)

        binned_unbinned_filtered_output_file_df = pd.concat([consensus_filtered_output_file_df, unbinned_list_df]).fillna('NA')
        
        # Reorder the columns
        column_order = ['virus_id', 'Type'] + [col for col in binned_unbinned_filtered_output_file_df.columns if col not in ['virus_id', 'Type']]
        binned_unbinned_filtered_output_file_df = binned_unbinned_filtered_output_file_df[column_order]
        binned_unbinned_filtered_output_file_df.drop(columns=['Sample', 'coordinates'], inplace=True)
        binned_unbinned_filtered_output_file_df.to_csv(binned_unbinned_filtered_output_file_path, sep='\t', index=False)

        return binned_unbinned_filtered_output_file_df


# Define a function to filter and update RPKM columns based on covered fraction
def filter_and_update_RPKM(row, cf, covered_fraction_cols, TPM_cols):
    for sample, cf_col in enumerate(covered_fraction_cols):
        cf_val = row[cf_col]
        if cf_val < cf:
            tpm_col = TPM_cols[sample]
            row[tpm_col] = 0
    return row

def create_coverage_tables(args, target_line, binned_unbinned_filtered_output_file_df, vBins_vOTUs_table_Folder_path):
    print(f"\n\033[1m{step_counter.print_main_step()}: Generating coverage output tables based on horizontal coverage values used in Module 05...\033[0m")

    # Extract the value of --covered-fraction from the target line
    covered_fraction_values = re.findall(r'--covered_fraction \[([^\]]+)\]', target_line)
    covered_fraction_values = list(map(float, covered_fraction_values[0].split(','))) if covered_fraction_values else None

    # Remove rows with Covered Fraction less than the specified value in each sample for each covered fraction value
    df_filtered_list = []
    
    for cf in covered_fraction_values:
        # Make a copy of df_filtered so that we don't modify it directly
        df_temp = binned_unbinned_filtered_output_file_df.copy()
        covered_fraction_cols = df_temp.filter(like='Covered Fraction').columns
        TPM_cols = df_temp.filter(like=args['normalization']).columns

        # Apply the filter_and_update_RPKM function to each row
        df_temp = df_temp.apply(filter_and_update_RPKM, args=(cf, covered_fraction_cols, TPM_cols), axis=1)

        # Filter out rows where all TPM values are 0
        df_temp = df_temp[~(df_temp[TPM_cols] == 0).all(axis=1)]
        df_temp = df_temp.loc[:, ~df_temp.columns.str.contains('Covered Fraction')]
        df_filtered_list.append(df_temp)

    # Save the filtered dataframes
    for i, cf in enumerate(covered_fraction_values):
        vBins_vOTUs_table_Files_path = os.path.join(vBins_vOTUs_table_Folder_path, f"MVP_07_Merged_vRhyme_Outputs_Filtered_{args['filtration']}_HC_{cf}_best_vBins_Representative_Unbinned_vOTUs_{args['normalization']}_Table.tsv")
        df_filtered_list[i].to_csv(vBins_vOTUs_table_Files_path, sep='\t', index=False)
        print(f"MVP_07_Merged_vRhyme_Outputs_Filtered_{args['filtration']}_HC_{cf}_best_vBins_Representative_Unbinned_vOTUs_{args['normalization']}_Table.tsv" + " saved in 07D_vBINS_vOTUS_TABLES")
        

def create_fasta_iphop_input(args, output_folder, binned_unbinned_filtered_output_file_df, fasta, output_folder_path, checkv_input_genome_vBins_fasta_file_path):
    fasta_iphop_input_Folder_path = os.path.join(output_folder, '07E_FASTA_IPHOP_INPUTS')
    if os.path.exists(fasta_iphop_input_Folder_path) and not args['force_outputs']:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping generating FASTA iPHoP inputs, folder already exists, and --force_outputs not provided...\033[0m")
    else:
        if os.path.exists(fasta_iphop_input_Folder_path):
            shutil.rmtree(fasta_iphop_input_Folder_path)
            os.makedirs(fasta_iphop_input_Folder_path)
        else:
            os.makedirs(fasta_iphop_input_Folder_path, exist_ok=True)

        binned_unbinned_filtered_prokaryote_unknown_iphop_input_file_path = os.path.join(fasta_iphop_input_Folder_path, f"MVP_07_Filtered_{args['filtration']}_Prokaryote_Unknown_Host_best_vBins_Representative_Unbinned_vOTUs_Sequences_iPHoP_Input.fasta")
        print(f"\n\033[1m{step_counter.print_sub_step()}: Generating {binned_unbinned_filtered_prokaryote_unknown_iphop_input_file_path}...\033[0m")
        prokaryote_unknown_sequences = binned_unbinned_filtered_output_file_df.loc[(binned_unbinned_filtered_output_file_df['Host type'] == 'Prokaryote') |
                                                                            (binned_unbinned_filtered_output_file_df['Host type'] == 'Unknown'), 'virus_id'].tolist()
        prokaryote_unknown_sequence_set = set(prokaryote_unknown_sequences)

        # Filter and write the sequences to the new FASTA file
        filtered_records_contigs = [record for record in SeqIO.parse(fasta, 'fasta') if record.id in prokaryote_unknown_sequence_set]
        filtered_records_checkv = [record for record in SeqIO.parse(checkv_input_genome_vBins_fasta_file_path, 'fasta') if record.id in prokaryote_unknown_sequence_set]
        filtered_records_vRhyme = []
        for filename in os.listdir(os.path.join(output_folder_path, 'vRhyme_best_bins_fasta')):
            if filename.endswith('.fasta'):
                bin_number = filename.split('_')[-1].split('.')[0]
                if 'vBin_' + bin_number in prokaryote_unknown_sequence_set:
                    vRhyme_vbin_fasta_filepath = os.path.join(output_folder_path, 'vRhyme_best_bins_fasta', filename)
                    filtered_records_vRhyme.extend(SeqIO.parse(vRhyme_vbin_fasta_filepath, 'fasta'))
        
        combined_records = filtered_records_contigs + filtered_records_checkv + filtered_records_vRhyme
        with open(binned_unbinned_filtered_prokaryote_unknown_iphop_input_file_path, 'w') as filtered_fasta:
            SeqIO.write(combined_records, filtered_fasta, 'fasta')

        binned_unbinned_filtered_prokaryote_iphop_input_file_path = os.path.join(fasta_iphop_input_Folder_path, f"MVP_07_Filtered_{args['filtration']}_Prokaryote_Host_Only_best_vBins_Representative_Unbinned_vOTUs_Sequences_iPHoP_Input.fasta")
        print(f"\n\033[1m{step_counter.print_sub_step()}: Generating {binned_unbinned_filtered_prokaryote_iphop_input_file_path}...\033[0m")

        prokaryote_sequences = binned_unbinned_filtered_output_file_df.loc[binned_unbinned_filtered_output_file_df['Host type'] == 'Prokaryote' , 'virus_id'].tolist()
        prokaryote_sequence_set = set(prokaryote_sequences)

        # Filter and write the sequences to the new FASTA file
        filtered_records_contigs = [record for record in SeqIO.parse(fasta, 'fasta') if record.id in prokaryote_sequence_set]
        filtered_records_checkv = [record for record in SeqIO.parse(checkv_input_genome_vBins_fasta_file_path, 'fasta') if record.id in prokaryote_sequence_set]
        filtered_records_vRhyme = []
        for filename in os.listdir(os.path.join(output_folder_path, 'vRhyme_best_bins_fasta')):
            if filename.endswith('.fasta'):
                bin_number = filename.split('_')[-1].split('.')[0]
                if 'vBin_' + bin_number in prokaryote_sequence_set:
                    vRhyme_vbin_fasta_filepath = os.path.join(output_folder_path, 'vRhyme_best_bins_fasta', filename)
                    filtered_records_vRhyme.extend(SeqIO.parse(vRhyme_vbin_fasta_filepath, 'fasta'))
        
        combined_records = filtered_records_contigs + filtered_records_checkv + filtered_records_vRhyme
        with open(binned_unbinned_filtered_prokaryote_iphop_input_file_path, 'w') as filtered_fasta:
            SeqIO.write(combined_records, filtered_fasta, 'fasta')


def create_vBin_summary_report(args, start_time, binned_unbinned_filtered_output_file_df, output_folder_path):
    print(f"\n\033[1m{step_counter.print_main_step()}: Creating summary report for Module 07...\033[0m")

    # Capture end time
    formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.now()
    formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate duration
    duration = end_time - start_time

    summary_report_path_module_07 = os.path.join(args['input'], '07_BINNING', 'MVP_07_Summary_Report.txt')

    # Statistics of filtered vBins
    filtered_vBin_df = binned_unbinned_filtered_output_file_df[binned_unbinned_filtered_output_file_df['Type'] == 'vBin']
    num_filtered_vBin = filtered_vBin_df['virus_id'].nunique()

    mean_filtered_vBin_length = filtered_vBin_df['virus_length'].mean()
    max_filtered_vBin_length = filtered_vBin_df['virus_length'].max()
    min_filtered_vBin_length = filtered_vBin_df['virus_length'].min()
    filtered_vBin_quality_counts = filtered_vBin_df['checkv_quality'].value_counts()

    # Count occurrences of each realm in the second level of the taxonomy column
    taxa_levels = filtered_vBin_df['taxonomy'].str.split(';')
    second_level_taxa = taxa_levels.apply(lambda x: x[1] if len(x) > 1 else 'Unclassified/others')
    taxa_counts = second_level_taxa.value_counts()
    # Calculate the percentage of each realm
    taxa_percentages = (taxa_counts / num_filtered_vBin) * 100
    # Prepare the summary report content
    taxa_summary = "\n".join([f"{realm}: {count} ({percentage:.1f}%)" for realm, count, percentage in zip(taxa_counts.index, taxa_counts.values, taxa_percentages.values)])

    # Prepare the summary report content for top classes
    taxa_levels = filtered_vBin_df['taxonomy'].str.split(';').apply(lambda levels: levels + [''] * (5 - len(levels)))
    fifth_level_classes = taxa_levels.apply(lambda x: x[4])
    filtered_classes = fifth_level_classes[(fifth_level_classes != '') & (fifth_level_classes != 'Unclassified')]
    class_counts = filtered_classes.value_counts()
    top_10_classes = class_counts.nlargest(10)
    top_classes_summary = "\n".join([f"{cls}: {count}" for cls, count in top_10_classes.items()])

    # Count the number of unbinned contigs
    unbinned_contig_df = binned_unbinned_filtered_output_file_df[binned_unbinned_filtered_output_file_df['Type'] == 'Unbinned_Contig']
    num_unbinned_contig = unbinned_contig_df['virus_id'].nunique()

    # Create a dictionary to hold argument descriptions and their default values
    argument_defaults = {
        '--input': args['input'],
        '--metadata': args['metadata'],
        '--binning_sample_group': args['binning_sample_group'],
        '--read_mapping_sample_group': args['read_mapping_sample_group'],
        '--keep_bam': args['keep_bam'],
        '--force_vrhyme': args['force_vrhyme'],
        '--force_checkv': args['force_checkv'],
        '--force_read_mapping': args['force_read_mapping'],
        '--interleaved': args['interleaved'],
        '--delete_files': args['delete_files'],
        '--normalization': args['normalization'],
        '--force_outputs': args['force_outputs'],
        '--filtration': args['filtration'],
        '--viral_min_genes': args['viral_min_genes'],
        '--host_viral_genes_ratio': args['host_viral_genes_ratio'],
        '--threads': args['threads']}

    # Write a summary line with script arguments and their default values
    summary_line = "07_do_binning.py"
    for arg, default in argument_defaults.items():
        if default is not None:
            summary_line += f" {arg} {default}"

    start_time = f"\nStart Time: {formatted_start_time}"
    end_time = f"End time: {formatted_end_time}"
    duration = f"Running Time: {duration.total_seconds():.2f} seconds\n"

    # Define the additional lines you want to add to the summary report
    module_07_summary_content = f"""
****************************************************************************
******************               MODULE 07                ******************
****************************************************************************

{summary_line}
{start_time}
{end_time}
{duration}

Summary Report after filtration
--------------------------
Number of filtered vBins: {num_filtered_vBin}
Mean vBin Length: {mean_filtered_vBin_length:.2f}
Max vBin Length: {max_filtered_vBin_length}
Min vBin Length: {min_filtered_vBin_length}

Filtered vBin CheckV quality summary:
Low Quality: {filtered_vBin_quality_counts.get('Low-quality', 0)}
Medium Quality: {filtered_vBin_quality_counts.get('Medium-quality', 0)}
High Quality: {filtered_vBin_quality_counts.get('High-quality', 0)}
Complete: {filtered_vBin_quality_counts.get('Complete', 0)}
Not determined: {filtered_vBin_quality_counts.get('Not-determined', 0)}

vOTUs taxonomy summary:
{taxa_summary}

Top 10 classes:
{top_classes_summary}

Number of unbinned viral contigs: {num_unbinned_contig}
        """
                
    # Write the content to the new summary report for Module 07
    with open(summary_report_path_module_07, 'w') as module_07_summary_report:
        module_07_summary_report.write(module_07_summary_content)

    message1 = "\033[1mModule 07 finished: vRhyme executed successfully!\033[0m\n"
    message2 = f"vRhyme outputs have been generated in {output_folder_path}.\n"
    message3 = f"Summary report for Module 07 has been created: summary_report_path_module_07)"
    line_of_stars = '*' * len(message3)
    print()
    print(line_of_stars)
    print(message1)
    print(f"Start Time: {formatted_start_time}") 
    print(f"End Time: {formatted_end_time}")
    print(f"Running Time: {duration}")
    print(duration)
    print(message2)
    print(message3)
    print(line_of_stars)
    print()

    print("Please don't forget to cite the following softwares used by this module:")
    print("- Kieft, K., Adams, A., Salamzade, R., Kalan, L., & Anantharaman, K. vRhyme enables binning of viral genomes from metagenomes. Nucleic Acids Research, 2022.\n")

def main(args): 
    # Capture start time
    start_time = datetime.datetime.now()
    formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nStart Time: {formatted_start_time}\n") 

    filtered_metadata_df, output_folder, fasta, bam_file_paths, output_folder_path = set_up_paths(args)

    vRhyme_output_files = binning_step(args, output_folder_path, fasta, bam_file_paths)

    membership_file = next((file for file in vRhyme_output_files if 'membership.tsv' in file), None)
    if membership_file is None or not os.path.exists(membership_file):

        empty_binning_summary_report(args, start_time, output_folder_path)
        
    else:
        checkv_output_directory_path, checkv_input_genome_vBins_fasta_file_path = checkv(args, output_folder, output_folder_path)

        read_mapping_vBins_directory, reference_path, vBins_fasta_files = generate_index(args, output_folder)

        coverM_vBins_output_file_df = read_mapping(args, output_folder, filtered_metadata_df, read_mapping_vBins_directory, reference_path, vBins_fasta_files)

        contig_summary_vRhyme_merged_df, unfiltered_output_read_mapping_file_df = merge_tables(args, output_folder_path, vRhyme_output_files, read_mapping_vBins_directory, checkv_output_directory_path, coverM_vBins_output_file_df)

        filtered_output_file_path, vBins_vOTUs_table_Folder_path, target_line, filtered_output_file_df = filter_tables(args, output_folder, unfiltered_output_read_mapping_file_df)  

        # Check if filtered_output_file_df is empty (just the header)
        if filtered_output_file_df.empty:

            empty_binning_after_filtration_summary_report(args, start_time, output_folder_path)

        else:
            consensus_filtered_output_file_df = find_taxonomy_consensus(unfiltered_output_read_mapping_file_df, filtered_output_file_df, filtered_output_file_path)

            binned_unbinned_filtered_output_file_df = combine_vBin_unbinned_tables(args, vBins_vOTUs_table_Folder_path, consensus_filtered_output_file_df, contig_summary_vRhyme_merged_df)

            create_coverage_tables(args, target_line, binned_unbinned_filtered_output_file_df, vBins_vOTUs_table_Folder_path)

            create_fasta_iphop_input(args, output_folder, binned_unbinned_filtered_output_file_df, fasta, output_folder_path, checkv_input_genome_vBins_fasta_file_path)

            create_vBin_summary_report(args, start_time, binned_unbinned_filtered_output_file_df, output_folder_path)
