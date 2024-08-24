import argparse
import glob
import os
import subprocess
import sys
from os.path import getsize
import pandas as pd
from functools import reduce
from Bio import SeqIO
from importlib_resources import files as resource_files
from tqdm import tqdm
import datetime
import time
import mvip

def fetch_arguments(parser):
    parser.set_defaults(func=main)
    parser.set_defaults(program="MVP_01_run_genomad_checkv")
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
        "--skip_modify_assemblies",
        action="store_true",
        default=False,
        help="Modify sequence headers by adding sample name, False by default.",
    )
    parser.add_argument(
        "--min_seq_size",
        type=int,
        default=0,
        help="Minimum sequence size to keep (in base pairs).",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--genomad_relaxed', help='Run geNomad with relaxed filtering.', action='store_true')
    group.add_argument('--genomad_conservative', help='Run geNomad with conservative filtering.', action='store_true')
    parser.add_argument('--genomad_db_path', help='Path to the geNomad database directory.', default='')
    parser.add_argument('--checkv_db_path', help='Path to the CheckV database directory.', default='')
    parser.add_argument('--force_genomad', help='Run geNomad even if output already exists.', action='store_true')
    parser.add_argument('--force_checkv', help='Run CheckV even if output already exists.', action='store_true')
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
    
# Define a function to find closest matching taxonomy and return Genome type and Host type
def find_closest_match(taxonomy, ictv_df):
    taxonomy_levels = taxonomy.split(';')
    matching_rows = []

    for i in range(len(taxonomy_levels), 0, -1):
        partial_taxonomy = ';'.join(taxonomy_levels[:i])
        match_rows = ictv_df[ictv_df['Family'] == partial_taxonomy]
        if not match_rows.empty:
            matching_rows.extend(match_rows.iterrows())

    if matching_rows:
        return matching_rows[0][1][['Genome type', 'Host type']]
    else:
        return pd.Series({'Genome type': 'Unknown', 'Host type': 'Unknown'})

# Define a function to map taxonomy to genome type
def taxon_to_genome_type(taxonomy, ictv_taxonomy_df):
    genome_host_info = find_closest_match(taxonomy, ictv_taxonomy_df)
    return genome_host_info['Genome type']

# Define a function to map taxonomy to host type
def taxon_to_host_type(taxonomy, ictv_taxonomy_df):
    genome_host_info = find_closest_match(taxonomy, ictv_taxonomy_df)
    return genome_host_info['Host type']

def rename_sequence(sequence_name):
    sequence_name = sequence_name.replace('provirus_', '')
    sequence_name = sequence_name.rsplit('/', 1)[0]
    sequence_name = sequence_name.replace('|', '_').replace('-', '_').replace('/', '_').replace(':', '_')
    return sequence_name

def rename_sequence_coord_checkv(virus_id):
    parts = virus_id.split('|')
    checkv = parts[-1]
    genomad = parts[-2]
    sequence_name = ""
    if genomad.startswith("provirus"): 
        tab_genomad = genomad.split('_')[1:3]
        tab_checkv = checkv.split('/')[0].split('-')
        if len(parts)>2:
            parts[0] = "_".join(parts[0:-2])  ## That is here in case there was some pipe in the original contig name
        tab_genomad[0] = str(int(tab_genomad[0]) + int(tab_checkv[0]) - 1)
        tab_genomad[1] = str(int(tab_genomad[0]) + int(tab_checkv[1]) - 1)
        sequence_name = parts[0] + '_' + "-".join(tab_genomad)
    else:
        tab_checkv = checkv.split('/')[0].split('-')
        if len(parts)>1:
            parts[0] = "_".join(parts[0:-1])  ## That is in case there was some pipe in the original contig name
        sequence_name = parts[0] + '_' + "-".join(tab_checkv)
    sequence_name = sequence_name.replace('|', '_').replace('-', '_').replace('/', '_').replace(':', '_')
    return sequence_name

def correct_coordinates(virus_id):
    tab_coords = virus_id.split('_')[-2:] ## So we simply take the last two fields when separating by "_"
    return "-".join(tab_coords)

def modify_assembly_files(input_assembly_file, sample_name, modified_assembly_dir, args):
    print(f"\n\033[1m{step_counter.print_main_step()}: Modifying the assembly files (adding sample name to headers and/or delete short sequences)...\033[0m")

    # Construct the new output file name in the modified assembly directory
    if args["skip_modify_assemblies"]:
        input_for_genomad = input_assembly_file
    else:
        output_assembly_file = os.path.join(modified_assembly_dir, f'{sample_name}_modified.fna')
        # Read sequences, modify headers, filter by size, and write to the new file
        sequences = []
        with open(input_assembly_file, "r") as input_fasta:
            for record in SeqIO.parse(input_fasta, "fasta"):
                # Modify the header by adding the sample name at the beginning
                new_header = f"{sample_name}_{record.id}"
                record.id = new_header
                record.description = new_header

                if len(record.seq) > args["min_seq_size"]:
                    sequences.append(record)

        # Write the modified and filtered sequences to the new file
        with open(output_assembly_file, "w") as output_fasta:
            SeqIO.write(sequences, output_fasta, 'fasta-2line')

        # Use the output_assembly_file for Genomad if it was modified
        input_for_genomad = output_assembly_file

    return input_for_genomad

def run_genomad_first_run(sample_name, input_for_genomad, genomad_output, args, genomad_db_path):
    if os.path.exists(genomad_output) and not args["force_genomad"]:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping running geNomad for {sample_name}, {genomad_output} folder already exists, and force_genomad not provided...\033[0m")
    else:
        if args["genomad_relaxed"]:
            print(f"\n\033[1m{step_counter.print_main_step()}: Running geNomad (relaxed mode) on {sample_name}...\033[0m")
            subprocess.run(['genomad', 'end-to-end', '--relaxed', '--cleanup', '--splits', '8', '-t', str(args["threads"]), input_for_genomad, genomad_output, genomad_db_path])
        elif args["genomad_conservative"]:
            print(f"\n\033[1m{step_counter.print_main_step()}: Running geNomad (conservative mode) on {sample_name}...\033[0m")
            subprocess.run(['genomad', 'end-to-end', '--conservative', '--cleanup', '--splits', '8', '-t', str(args["threads"]), input_for_genomad, genomad_output, genomad_db_path])
        else:
            print(f"\n\033[1m{step_counter.print_main_step()}: Running geNomad (normal mode) on {sample_name}...\033[0m")
            subprocess.run(['genomad', 'end-to-end', '--cleanup', '--splits', '8', '-t', str(args["threads"]), input_for_genomad, genomad_output, genomad_db_path])

def run_checkv_first_run(sample_name, genomad_output, checkv_db_path, checkv_sample_directory, args):
    checkv_input_files = glob.glob(os.path.join(genomad_output, '**/*_virus.fna'))
    checkv_input = checkv_input_files[0]
    checkv_output = os.path.join(checkv_sample_directory, f'{sample_name}_Viruses_CheckV_Output')
    virus_checkv_file = os.path.join(args["input"], '02_CHECK_V', str(sample_name), f'{sample_name}_Viruses_CheckV_Output/quality_summary.tsv')
    
    if os.path.exists(virus_checkv_file) and not args["force_checkv"]:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping CheckV for {sample_name}, {checkv_output} folder already exists, and force_checkv not provided...\033[0m")
        df_virus_CHECKV = pd.read_csv(virus_checkv_file, sep='\t', usecols=['contig_id', 'contig_length', 'provirus', 'proviral_length', 'gene_count', 'viral_genes',
                                                                         'host_genes', 'checkv_quality', 'miuvig_quality', 'completeness', 'completeness_method', 'kmer_freq'])
    else:
        if getsize(checkv_input) == 0:
            print(f"\n\033[1m{step_counter.print_main_step()}: Skipping CheckV {checkv_input} because it is empty...\033[0m")
            # Create output folder for skipped files
            empty_checkv_output = os.path.join(checkv_output)
            os.makedirs(empty_checkv_output, exist_ok=True)
            # Write skipped_files.txt in the skipped folder
            with open(os.path.join(empty_checkv_output, 'Virus_CheckV_logfile.txt'), 'a') as f:
                f.write('Creating empty virus.fna and quality_summary.tsv')
            # Create empty viruses.fna and proviruses.fna files
            with open(os.path.join(empty_checkv_output, 'viruses.fna'), 'w') as f:
                pass
            with open(os.path.join(empty_checkv_output, 'proviruses.fna'), 'w') as f:
                pass
            with open(os.path.join(empty_checkv_output, 'quality_summary.tsv'), 'w') as f:
                f.write('contig_id\tcontig_length\tprovirus\tproviral_length\tgene_count\tviral_genes\thost_genes\tcheckv_quality\tmiuvig_quality\tcompleteness\tcompleteness_method\tcontamination\tkmer_freq\twarnings\n')
            df_virus_CHECKV = pd.read_csv(virus_checkv_file, sep='\t', usecols=['contig_id', 'contig_length', 'provirus', 'proviral_length', 'gene_count', 'viral_genes',
                                                                         'host_genes', 'checkv_quality', 'miuvig_quality', 'completeness', 'completeness_method', 'kmer_freq'])
        else:
            print(f"\n\033[1m{step_counter.print_main_step()}: Running CheckV on {sample_name}...\033[0m")
            subprocess.run(['checkv', 'end_to_end', checkv_input, checkv_output, '-d', checkv_db_path, '-t', str(args["threads"]), '--remove_tmp'])
            genomad_proviruses_input = os.path.join(checkv_output, 'proviruses.fna')
            new_genomad_proviruses_input = genomad_proviruses_input + '.new'
            with open(genomad_proviruses_input, 'r') as f_in, open(new_genomad_proviruses_input, 'w') as f_out:
                for line in f_in:
                    if line.startswith('>'):
                        # Adjust contig name here, to reflect actual coordinates if this is a double provirus (Genomad provirus trimmed by CheckV)
                        new_header = rename_sequence_coord_checkv(line.strip().replace(' ', '|'))
                        f_out.write(new_header + '\n')
                    else:
                        f_out.write(line)
            # Replace the original file with the modified file
            os.replace(new_genomad_proviruses_input, genomad_proviruses_input)
            df_virus_CHECKV = pd.read_csv(virus_checkv_file, sep='\t', usecols=['contig_id', 'contig_length', 'provirus', 'proviral_length', 'gene_count', 'viral_genes',
                                                                         'host_genes', 'checkv_quality', 'miuvig_quality', 'completeness', 'completeness_method', 'kmer_freq'])

    return df_virus_CHECKV

def run_genomad_second_run(sample_name, checkv_output, genomad_sample_directory, args, genomad_db_path):
    genomad_proviruses_input = os.path.join(checkv_output, 'proviruses.fna')
    genomad_proviruses_output = os.path.join(genomad_sample_directory, f'{sample_name}_Proviruses_Genomad_Output')

    if os.path.exists(genomad_proviruses_output) and not args["force_genomad"]:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping Genomad on proviruses for {sample_name}, {genomad_proviruses_output} folder already exists, and force_genomad not provided...\033[0m")
    else:
        if getsize(genomad_proviruses_input) == 0:
            print(f"\n\033[1m{step_counter.print_main_step()}: Skipping Genomad on proviruses {genomad_proviruses_input} because it is empty...\033[0m")
            # Create output folder for skipped files
            empty_genomad_proviruses_output = os.path.join(genomad_proviruses_output, 'proviruses_summary')
            os.makedirs(empty_genomad_proviruses_output, exist_ok=True)
            # Write skipped_files.txt in the skipped folder
            with open(os.path.join(empty_genomad_proviruses_output, 'Provirus_Genomad_logfile.txt'), 'a') as f:
                f.write('Creating empty proviruses_virus.fna and proviruses_virus_summary.tsv')
            # Create empty viruses.fna file
            with open(os.path.join(empty_genomad_proviruses_output, 'proviruses_virus.fna'), 'w') as f:
                pass
            with open(os.path.join(empty_genomad_proviruses_output, 'proviruses_virus_summary.tsv'), 'w') as f:
                f.write('seq_name\tlength\ttopology\tcoordinates\tn_genes\tgenetic_code\tvirus_score\tfdr\tn_hallmarks\tmarker_enrichment\ttaxonomy\n')
        else:
            print(f"\n\033[1m{step_counter.print_main_step()}: Running Genomad on proviruses {sample_name}...\033[0m")
            subprocess.run(['genomad', 'end-to-end', '--min-virus-hallmarks-short-seqs', '1', '--min-score', '0.5', '--cleanup', '--splits', '8', '-t', str(args["threads"]), genomad_proviruses_input, genomad_proviruses_output, genomad_db_path])

def run_checkv_second_run(sample_name, checkv_sample_directory, genomad_proviruses_output, args, checkv_db_path):
    checkv_proviruses_input = os.path.join(genomad_proviruses_output, 'proviruses_summary', 'proviruses_virus.fna')
    checkv_proviruses_output = os.path.join(checkv_sample_directory, f'{sample_name}_Proviruses_CheckV_Output')
    provirus_checkv_file = os.path.join(args["input"], '02_CHECK_V', str(sample_name), f'{sample_name}_Proviruses_CheckV_Output/quality_summary.tsv')

    if os.path.exists(provirus_checkv_file) and not args["force_checkv"]:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping CheckV on proviruses for {sample_name}, {checkv_proviruses_output} folder already exists, and force_checkv not provided...\033[0m")
    else:
        if getsize(checkv_proviruses_input) == 0:
            print(f"\n\033[1m{step_counter.print_main_step()}: Skipping CheckV on {checkv_proviruses_input} because it is empty...\033[0m")
            # Create output folder for skipped files
            os.makedirs(checkv_proviruses_output, exist_ok=True)
            # Write skipped_files.txt in the skipped folder
            with open(os.path.join(checkv_proviruses_output, 'Provirus_CheckV_logfile.txt'), 'a') as f:
                f.write('Creating empty viruses.fna and quality_summary.tsv')
            # Create empty viruses.fna file
            with open(os.path.join(checkv_proviruses_output, 'viruses.fna'), 'w') as f:
                pass
            with open(os.path.join(checkv_proviruses_output, 'quality_summary.tsv'), 'w') as f:
                f.write('contig_id\tcontig_length\tprovirus\tproviral_length\tgene_count\tviral_genes\thost_genes\tcheckv_quality\tmiuvig_quality\tcompleteness\tcompleteness_method\tcontamination\tkmer_freq\twarnings\n')
        else:
            print(f"\n\033[1m{step_counter.print_main_step()}: Running CheckV on proviruses {sample_name}...\033[0m")
            subprocess.run(['checkv', 'end_to_end', checkv_proviruses_input, checkv_proviruses_output, '-d', checkv_db_path, '-t', str(args["threads"]), '--remove_tmp'])

        # Open the quality summary file for reading
        with open(provirus_checkv_file, 'r') as f:
            lines = f.readlines()

        # Find the index of the 'provirus' column
        header = lines[0].strip().split('\t')
        provirus_col_index = header.index('provirus')

        # Modify the lines where provirus is 'No' to 'Yes'
        for i in range(1, len(lines)):
            fields = lines[i].strip().split('\t')
            if fields[provirus_col_index] == 'No':
                fields[provirus_col_index] = 'Yes'
                lines[i] = '\t'.join(fields) + '\n'

        # Write the modified lines to the original file
        with open(provirus_checkv_file, 'w') as f:
            f.writelines(lines)

def create_tables(sample_name, df_virus_CHECKV, df_provirus_CHECKV, df_virus_GENOMAD, df_provirus_GENOMAD, args):
    print(f"\n\033[1m{step_counter.print_main_step()}: Creating merged unfiltered virus-provirus Genomad-CheckV output tables for {sample_name}...\033[0m")
    
    # Construct the path to the ICTV_Taxonomy_List.tsv file
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # Get the directory of the mvp directory
    mvp_directory = os.path.dirname(script_directory)
    # Load the ICTV Taxonomy List file
    ictv_taxonomy_file = os.path.join(mvp_directory, 'data', 'ICTV_Taxonomy_List.tsv')
    # Read the ICTV Taxonomy List file
    ictv_taxonomy_df = pd.read_csv(ictv_taxonomy_file, sep='\t')

    # Filter out provirus lines in df_virus_CHECKV
    df_virus_CHECKV = df_virus_CHECKV[df_virus_CHECKV['provirus'] != 'Yes']

    # Merge the filtered virus CheckV and proviruses CheckV DataFrames
    checkv_merged_df = pd.concat([df_virus_CHECKV, df_provirus_CHECKV], ignore_index=True)

    # Merge the virus Genomad and proviruses Genomad DataFrames
    genomad_merged_df = pd.concat([df_virus_GENOMAD, df_provirus_GENOMAD], ignore_index=True)

    # Merge the merged CheckV and the merged Genomad DataFrames
    checkv_genomad_merged_df = pd.merge(checkv_merged_df, genomad_merged_df, left_on='contig_id',right_on='seq_name', how='left')
    checkv_genomad_merged_df = checkv_genomad_merged_df.rename(columns={'contig_id': 'virus_id', 'contig_length': 'virus_length'}).drop('proviral_length', axis=1)

    # Cast the 'topology' column to string type
    checkv_genomad_merged_df['topology'] = checkv_genomad_merged_df['topology'].astype(str)
    checkv_genomad_merged_df['virus_id'] = checkv_genomad_merged_df['virus_id'].astype(str)

    # Copy over the number of genes from genomad ('n_genes) in the column 'gene_count' that is derived from CheckV
    checkv_genomad_merged_df['gene_count'] = checkv_genomad_merged_df['n_genes']

    # Remove the redundant column
    checkv_genomad_merged_df.drop(['n_genes'], inplace=True, axis=1)

    # Update the 'provirus' column for rows where 'topology' contains 'Provirus'
    checkv_genomad_merged_df.loc[checkv_genomad_merged_df['topology'].str.contains('Provirus'), 'provirus'] = 'Yes'

    # Change 'No terminal repeats' to 'Provirus' for rows where 'Yes' is present in the 'provirus' column
    checkv_genomad_merged_df.loc[checkv_genomad_merged_df['provirus'] == 'Yes', 'topology'] = checkv_genomad_merged_df.loc[checkv_genomad_merged_df['provirus'] == 'Yes', 'topology'].replace('No terminal repeats', 'Provirus')
    checkv_genomad_merged_df = checkv_genomad_merged_df.fillna('NA')

    # Apply functions to each row in checkv_genomad_merged_df
    checkv_genomad_merged_df['Genome type'] = checkv_genomad_merged_df['taxonomy'].apply(lambda x: taxon_to_genome_type(x, ictv_taxonomy_df))
    checkv_genomad_merged_df['Host type'] = checkv_genomad_merged_df['taxonomy'].apply(lambda x: taxon_to_host_type(x, ictv_taxonomy_df))

    # Exclude specific columns before saving the DataFrame
    columns_to_exclude = ['seq_name', 'topology']  
    checkv_genomad_merged_df = checkv_genomad_merged_df.drop(columns=columns_to_exclude)

    # Save the merged Checkv and Genomad file
    checkv_genomad_merged_output_file = os.path.join(args["input"], '02_CHECK_V', str(sample_name), f'MVP_01_{sample_name}_Unfiltered_Merged_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv')

    # Add a 'Sample' column with the current sample name
    checkv_genomad_merged_df.insert(0, 'Sample', sample_name)

    # Apply renaming logic to the 'virus_id' column
    checkv_genomad_merged_df['virus_id'] = checkv_genomad_merged_df['virus_id'].apply(rename_sequence)

    ## Note: the CheckV provirus would already be "clean" so this renaming should not affect them
    checkv_genomad_merged_df.to_csv(checkv_genomad_merged_output_file, sep='\t', index=False)

def generate_summary_report(args, sample_name, formatted_start_time, formatted_end_time, duration, genomad_sample_directory):
    print(f"\n\033[1m{step_counter.print_main_step()}: Generating summary reports for {sample_name}...\033[0m")
   
    # Define the lines you want to add
    module_01_header = """****************************************************************************
******************               MODULE 01                ******************
****************************************************************************
"""

    # Create a dictionary to hold argument descriptions and their default values
    argument_defaults = {
        '--input': args["input"],
        '--metadata': args["metadata"],
        '--genomad-relaxed': args["genomad_relaxed"],
        '--genomad-conservative': args["genomad_conservative"],
        '--sample-group': args["sample_group"],
        '--skip_modify_assemblies': args["skip_modify_assemblies"],
        '--min-seq-size': args["min_seq_size"],
        '--threads': args["threads"]}

    # Write a summary line with script arguments and their default values
    summary_line = "01_run_genomad_checkv.py"
    for arg, default in argument_defaults.items():
        if default is not None:
            summary_line += f" {arg} {default}"

    # Specify the path for the new MVP_01_Summary_Report.txt in '01_GENOMAD' directory
    summary_report_01_path = os.path.join(genomad_sample_directory, str(sample_name) + '_MVP_01_Summary_Report.txt')

    # Write the modified content to the new summary report in '01_GENOMAD'
    formatted_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    duration = datetime.datetime.now() - datetime.datetime.now()
    with open(summary_report_01_path, 'w') as summary_report:
        summary_report.write(module_01_header + summary_line)
        summary_report.write(f"\n")
        summary_report.write(f"\nStart Time: {formatted_start_time}\n")
        summary_report.write(f"End time: {formatted_end_time}\n")
        summary_report.write(f"Running Time: {duration.total_seconds():.2f} seconds\n")

def main(args):
    # Capture start time
    mvp_start_time = datetime.datetime.now()
    mvp_formatted_start_time = mvp_start_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nStart Time: {mvp_formatted_start_time}") 

    # read metadata file and map FASTQ files
    metadata = pd.read_csv(args["metadata"], sep='\t')

    # Determine the geNomad database path
    genomad_db_path = os.path.join(args["input"], '00_DATABASES', 'genomad_db')
    if args["genomad_db_path"]:
        genomad_db_path = args["genomad_db_path"]

    # Determine the checkV database path
    checkv_db_path = os.path.join(args["input"], '00_DATABASES', 'checkv-db-v1.5')
    if args["checkv_db_path"]:
        checkv_db_path = args["checkv_db_path"]

    # Create a new directory for modified and filtered assembly files
    if not args["skip_modify_assemblies"]:
        modified_assembly_dir = os.path.join(args["input"], '00_MODIFIED_ASSEMBLY_FILES')
        os.makedirs(modified_assembly_dir, exist_ok=True)
    else: 
        modified_assembly_dir = None

    # Process rows based on specific sample numbers or all rows
    specific_sample_numbers = []
    if args["sample_group"]:
        specific_sample_numbers = [int(num) for num in args["sample_group"].split(',') if num.strip()]


    for row_index, (_, row) in enumerate(metadata.iterrows(), start=1):
        input_assembly_file = row['Assembly_Path']
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

        input_for_genomad = modify_assembly_files(input_assembly_file, sample_name, modified_assembly_dir, args)

        # Create directories for the current sample in 01_GENOMAD and 02_CHECK_V
        genomad_sample_directory = os.path.join(args["input"], '01_GENOMAD', str(sample_name))
        os.makedirs(genomad_sample_directory, exist_ok=True)
        checkv_sample_directory = os.path.join(args["input"], '02_CHECK_V', str(sample_name))
        os.makedirs(checkv_sample_directory, exist_ok=True)

        genomad_output = os.path.join(genomad_sample_directory, f'{sample_name}_Viruses_Genomad_Output')
        checkv_output = os.path.join(checkv_sample_directory, f'{sample_name}_Viruses_CheckV_Output')
        genomad_proviruses_output = os.path.join(genomad_sample_directory, f'{sample_name}_Proviruses_Genomad_Output')

        run_genomad_first_run(sample_name, input_for_genomad, genomad_output, args, genomad_db_path)

        virus_genomad_file = glob.glob(os.path.join(args["input"], '01_GENOMAD', str(sample_name), f'{sample_name}_Viruses_Genomad_Output/*/*_virus_summary.tsv'))[0]
        df_virus_GENOMAD = pd.read_csv(virus_genomad_file, sep='\t', usecols=['seq_name', 'topology', 'n_genes', 'genetic_code', 'virus_score', 'n_hallmarks', 'marker_enrichment', 'taxonomy', 'coordinates'])
       
        run_checkv_first_run(sample_name, genomad_output, checkv_db_path, checkv_sample_directory, args)
        virus_checkv_file = os.path.join(args["input"], '02_CHECK_V', str(sample_name), f'{sample_name}_Viruses_CheckV_Output/quality_summary.tsv')
        df_virus_CHECKV = pd.read_csv(virus_checkv_file, sep='\t', usecols=['contig_id', 'contig_length', 'provirus', 'proviral_length', 'gene_count', 'viral_genes',
                                                                         'host_genes', 'checkv_quality', 'miuvig_quality', 'completeness', 'completeness_method', 'kmer_freq'])
      
        run_genomad_second_run(sample_name, checkv_output, genomad_sample_directory, args, genomad_db_path)
        provirus_genomad_file = glob.glob(os.path.join(args["input"], '01_GENOMAD', str(sample_name), f'{sample_name}_Proviruses_Genomad_Output/*/proviruses_virus_summary.tsv'))[0]
        df_provirus_GENOMAD = pd.read_csv(provirus_genomad_file, sep='\t', usecols=['seq_name', 'topology', 'n_genes', 'genetic_code', 'virus_score', 'n_hallmarks', 'marker_enrichment', 'taxonomy', 'coordinates'])
        # Correct the coordinates, since these are actually proviruses we reprocessed
        df_provirus_GENOMAD['coordinates'] = df_provirus_GENOMAD['seq_name'].apply(lambda x: correct_coordinates(x))

        run_checkv_second_run(sample_name, checkv_sample_directory, genomad_proviruses_output, args, checkv_db_path)
        provirus_checkv_file = os.path.join(args["input"], '02_CHECK_V', str(sample_name), f'{sample_name}_Proviruses_CheckV_Output/quality_summary.tsv')
        df_provirus_CHECKV = pd.read_csv(provirus_checkv_file, sep='\t', usecols=['contig_id', 'contig_length', 'provirus', 'proviral_length', 'gene_count', 'viral_genes', 'host_genes', 'checkv_quality', 'miuvig_quality', 'completeness', 'completeness_method', 'kmer_freq'])
     
        create_tables(sample_name, df_virus_CHECKV, df_provirus_CHECKV, df_virus_GENOMAD, df_provirus_GENOMAD, args)

        # Capture end time
        end_time = datetime.datetime.now()
        formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

        # Calculate duration
        duration = end_time - start_time

        generate_summary_report(args, sample_name, formatted_start_time, formatted_end_time, duration, genomad_sample_directory)

        print(f"\nEnd Time of processing {sample_name}: {formatted_end_time}")
        print(f"Running Time of processing {sample_name}: {duration.total_seconds():.2f} seconds")
        
    # Capture end time
    mvp_end_time = datetime.datetime.now()
    mvp_formatted_end_time = mvp_end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate duration
    mvp_duration = mvp_end_time - mvp_start_time
    
    message1 = "\033[1mModule 01 finished: geNomad and CheckV executed successfully!\033[0m\n"
    message2 = "geNomad and CheckV output directories for both viruses and proviruses have been generated."
    message3 = "You can look in <sample_name>_virus_summary.tsv, proviruses_virus_summary.tsv, and quality_summary.tsv tabular files for a summary of geNomad and CheckV outputs."
    message4 = "\n\033[1mYou can now proceed to the next step of the MVP script: Module 02!\033[0m"
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

    print("Please don't forget to cite MVP and the following softwares used by this module:")
    print("- Camargo, A. P., Roux, S., Schulz, F., Babinski, M., Xu, Y., Hu, B., Chain, P. S. G., Nayfach, S., & Kyrpides, N. C. Identification of mobile genetic elements with geNomad. Nat Biotechnol, 1-10 (2023). https://doi.org/10.1038/s41587-023-01953-y")
    print("\n- Nayfach, S., Camargo, A.P., Schulz, F. et al. CheckV assesses the quality and completeness of metagenome-assembled viral genomes. Nat Biotechnol 39, 578–585 (2021). https://doi.org/10.1038/s41587-020-00774-7\n")
