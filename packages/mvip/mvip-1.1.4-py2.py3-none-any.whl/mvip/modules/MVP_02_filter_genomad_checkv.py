import argparse
import glob
import os
import sys
import pandas as pd
from Bio import SeqIO
import datetime
import time
import mvip

def fetch_arguments(parser):
    parser.set_defaults(func=main)
    parser.set_defaults(program="MVP_02_filter_genomad_checkv")
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
        "--viral_min_genes",
        type=int,
        default=1,
        help="the minimum number of viral genes required to consider a row as a virus prediction (default = 1)",
    )
    parser.add_argument(
        "--host_viral_genes_ratio",
        type=int,
        default=1,
        help="the maximum ratio of host genes to viral genes required to consider a row as a virus prediction (default = 1",
    )

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

def rename_sequence(sequence_name):
    sequence_name = sequence_name.replace('provirus_', '')
    sequence_name = sequence_name.rsplit('/', 1)[0]
    sequence_name = sequence_name.replace('|', '_').replace('-', '_').replace('/', '_').replace(':', '_')
    return sequence_name

def merge_tables(sample_name, args):
    print(f"\n\033[1m{step_counter.print_main_step()}: Merging the geNomad and CheckV output tables...\033[0m")
    # Construct the path to the quality_summary.tsv file based on the sample name
    unfiltered_virus_provirus_genomad_checkv_path = os.path.join(args["input"], '02_CHECK_V', str(sample_name), f'MVP_01_{sample_name}_Unfiltered_Merged_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv')
    unfiltered_virus_provirus_genomad_checkv_df = pd.read_csv(unfiltered_virus_provirus_genomad_checkv_path, sep='\t')

    # Filter the merged dataframe to keep only rows predicted as 'virus'
    filtered_virus_provirus_genomad_checkv_df = unfiltered_virus_provirus_genomad_checkv_df.loc[(unfiltered_virus_provirus_genomad_checkv_df['viral_genes'] >= args["viral_min_genes"])]
    filtered_virus_provirus_genomad_checkv_df = filtered_virus_provirus_genomad_checkv_df.loc[filtered_virus_provirus_genomad_checkv_df['host_genes'] / filtered_virus_provirus_genomad_checkv_df['viral_genes'] <= args["host_viral_genes_ratio"]]

    # Save the merged Checkv and Genomad file
    filtered_virus_provirus_genomad_checkv_path = os.path.join(args["input"], '02_CHECK_V', str(sample_name), f'MVP_02_{sample_name}_Filtered_Relaxed_Merged_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv')
    filtered_virus_provirus_genomad_checkv_df.to_csv(filtered_virus_provirus_genomad_checkv_path, sep='\t', index=False)

    return filtered_virus_provirus_genomad_checkv_df

def generate_fasta_files(virus_fasta_file, provirus_fasta_file, sample_name, args, virus_ids_to_keep, rename_sequence):
    print(f"\n\033[1m{step_counter.print_sub_step()}: Creating the unfiltered FASTA file containing virus and provirus sequences...\033[0m")
    virus_fasta_lines = []
    provirus_fasta_lines = []

    if os.path.isfile(virus_fasta_file):
        with open(virus_fasta_file, 'r') as f:
            virus_fasta_lines = f.readlines()

    if os.path.isfile(provirus_fasta_file):
        with open(provirus_fasta_file, 'r') as f:
            provirus_fasta_lines = f.readlines()

    # Concatenate the virus and provirus fasta sequences
    concatenated_fasta_lines = virus_fasta_lines + provirus_fasta_lines

    # Concatenated FASTA file
    concatenated_fasta_file = os.path.join(args["input"], '02_CHECK_V', str(sample_name), f'MVP_02_{sample_name}_Unfiltered_Virus_Provirus_Sequences.fna')
    
    # Open the input file and create a list to store modified sequences
    with open(concatenated_fasta_file, 'w') as f:
        for line in concatenated_fasta_lines:
            if line.startswith('>'):
                contig_id = line.strip()[1:]
                # Use the rename_sequence function here
                renamed_contig_id = rename_sequence(contig_id)
                write_line = True
                f.write(f'>{renamed_contig_id}\n')
            else:
                if write_line:
                    f.write(line)

    # Open the concatenated file and read the lines
    with open(concatenated_fasta_file, 'r') as input_file:
        concatenated_fasta_lines = input_file.readlines()

    print(f"\n\033[1m{step_counter.print_sub_step()}: Creating the filtered FASTA file containing virus and provirus sequences...\033[0m")
    # Filter the concatenated file
    filtered_concatenated_fasta_file = os.path.join(args["input"], '02_CHECK_V', str(sample_name), f'MVP_02_{sample_name}_Filtered_Relaxed_Virus_Provirus_Sequences.fna')
    
    # Open the output file for writing the filtered sequences
    with open(filtered_concatenated_fasta_file, 'w') as output_file:
        write_line = False  # Initialize the flag
        for line in concatenated_fasta_lines:
            if line.startswith('>'):
                contig_id = line.strip()[1:]
                if contig_id in virus_ids_to_keep:
                    write_line = True
                    output_file.write(line)
                else:
                    write_line = False
            else:
                if write_line:
                    output_file.write(line)

def generate_summary_report(args, sample_name, formatted_start_time, formatted_end_time, duration):
    print(f"\n\033[1m{step_counter.print_main_step()}: Generating summary report for {sample_name}...\033[0m")
   
    # Define the lines you want to add
    module_02_header = """****************************************************************************
******************               MODULE 02                ******************
****************************************************************************
"""

    # Create a dictionary to hold argument descriptions and their default values
    argument_defaults = {
        '--input': args["input"],
        '--metadata': args["metadata"],
        '--sample-group': args["sample_group"],
        '--viral-min-genes': args["viral_min_genes"],
        '--host-viral-genes-ratio': args["host_viral_genes_ratio"]}

    # Write a summary line with script arguments and their default values
    summary_line = "02_filter_genomad_checkv.py"
    for arg, default in argument_defaults.items():
        if default is not None:
            summary_line += f" {arg} {default}"

    # Specify the path for the new MVP_01_Summary_Report.txt in '01_GENOMAD' directory
    summary_report_02_path = os.path.join(args["input"], '02_CHECK_V', str(sample_name), str(sample_name) + '_MVP_02_Summary_Report.txt')

    # Write the modified content to the new summary report in '01_GENOMAD'
    with open(summary_report_02_path, 'w') as summary_report:
        summary_report.write(module_02_header + summary_line)
        summary_report.write(f"\n")
        summary_report.write(f"\nStart Time: {formatted_start_time}\n")
        summary_report.write(f"End time: {formatted_end_time}\n")
        summary_report.write(f"Running Time: {duration.total_seconds():.2f} seconds\n")

    print("Summary report for Module 02 has been created: ", summary_report_02_path)
    print(f"\nEnd Time of processing {sample_name}: {formatted_end_time}")
    print(f"Running Time of processing {sample_name}: {duration.total_seconds():.2f} seconds")

def main(args):
    # Capture start time
    mvp_start_time = datetime.datetime.now()
    mvp_formatted_start_time = mvp_start_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nStart Time: {mvp_formatted_start_time}") 

    # read metadata file and map FASTQ files
    metadata = pd.read_csv(args["metadata"], sep='\t')

    # Process rows based on specific sample numbers or all rows
    specific_sample_numbers = []
    if args["sample_group"]:
        specific_sample_numbers = [int(num) for num in args["sample_group"].split(',') if num.strip()]

    for row_index, (_, row) in enumerate(metadata.iterrows(), start=1):
        sample_number = row['Sample_number']
        sample_name = row['Sample']

        # Check if the current sample number is in the list of specific sample numbers
        if specific_sample_numbers and sample_number not in specific_sample_numbers:
            continue # Skip to the next iteration

        step_counter.reset()

        # Capture start time
        start_time = datetime.datetime.now()
        formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\nStart Time of processing {sample_name}: {formatted_start_time}") 

        filtered_virus_provirus_genomad_checkv_df = merge_tables(sample_name, args)

        virus_ids_to_keep = set(filtered_virus_provirus_genomad_checkv_df['virus_id'].tolist())

        # Concatenated FASTA sequences
        virus_fasta_file = glob.glob(os.path.join(args["input"], '02_CHECK_V', str(sample_name), f'{sample_name}_Viruses_CheckV_Output/viruses.fna'))[0]
        provirus_fasta_file = glob.glob(os.path.join(args["input"], '02_CHECK_V', str(sample_name), f'{sample_name}_Proviruses_CheckV_Output/viruses.fna'))[0]

        generate_fasta_files(virus_fasta_file, provirus_fasta_file, sample_name, args, virus_ids_to_keep, rename_sequence)
        
        # Capture end time
        end_time = datetime.datetime.now()
        formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

        # Calculate duration
        duration = end_time - start_time

        # Define the additional lines you want to add to the summary report
        generate_summary_report(args, sample_name, formatted_start_time, formatted_end_time, duration)

    # Capture end time
    mvp_end_time = datetime.datetime.now()
    mvp_formatted_end_time = mvp_end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate duration
    mvp_duration = mvp_end_time - mvp_start_time

    message1 = "\033[1mModule 02 finished: output summary files merged and filtered successfully!\033[0m\n"
    message2 = "Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv and viruses_proviruses.fna files have been generated for each sample in their respective directories in 02_CHECK_V."
    message3 = "viruses_proviruses.fna files will be used to run Module 03 (clustering)."
    message4 = "\n\033[1mYou can now proceed to the next step of the MVP script: Module 03!\033[0m"
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
    print(line_of_stars)
    print()

    print("Please don't forget to cite MVP.")