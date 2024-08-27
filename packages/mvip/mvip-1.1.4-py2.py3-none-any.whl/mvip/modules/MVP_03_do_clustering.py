import argparse
import os
import subprocess
import pandas as pd
import glob
import shutil
import re
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
import datetime
import time
import mvip

def fetch_arguments(parser):
    parser.set_defaults(func=main)
    parser.set_defaults(program="MVP_03_do_clustering")
    parser.add_argument(
        "--input", "-i",
        help="Path to your working directory where you want to run MVP.",
    )
    parser.add_argument(
        "--metadata", "-m",
        help="Path to your metadata that you want to use to run MVP.",
    )
    parser.add_argument(
        "--min_ani",
        type=int,
        default=95,
        help="Minimum ANI value for clustering (default = 95)",
    )
    parser.add_argument(
        "--min_tcov",
        type=int,
        default=85,
        help="Minimum coverage of the target sequence (default = 85)",
    )
    parser.add_argument(
        "--min_qcov",
        type=int,
        default=0,
        help="Minimum coverage of the query sequence (default = 0)",
    )
    parser.add_argument(
        "--read-type",
        type=str,
        default='short',
        help="Sequencing data type (e.g. short vs long reads). Default = short",
    )
    parser.add_argument(
        "--unfiltered_protein_file",
        action="store_true",
        default=False,
        help="Create protein FASTA file from unfiltered virus sequence. Default = False. Warning = If argument provided, the script might run for a long period of time.",
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

def rename_sequence(sequence_name):
    sequence_name = sequence_name.replace('provirus_', '')
    sequence_name = sequence_name.rsplit('/', 1)[0]
    sequence_name = sequence_name.replace('|', '_').replace('-', '_').replace('/', '_').replace(':', '_')
    return sequence_name

def rename_protein_sequence(sequence_name):
    original_sequence_name = sequence_name  # Store the original sequence name
    sequence_name = sequence_name.replace('provirus_', '')
    if ' ' in sequence_name:
        sequence_name, additional_info = sequence_name.split(' ', 1)
    else:
        additional_info = ''

    sequence_name = re.sub(r'\/\w+_(\w+)', r'_\1', sequence_name)
    sequence_name = sequence_name.replace('|', '_').replace('-', '_').replace('/', '_').replace(':', '_')

    additional_parts = additional_info.split(' ')
    if len(additional_parts) > 1:
        additional_parts[0] = '_'.join(part.strip() for part in additional_parts[0].split('_'))

    modified_sequence_name = f"{sequence_name} {' '.join(additional_parts)}"

    return f"{modified_sequence_name} {original_sequence_name}"

def rename_protein_sequence_table(sequence_name):
    sequence_name = sequence_name.replace('provirus_', '')
    sequence_name = re.sub(r'\/\w+_(\w+)', r'_\1', sequence_name)
    sequence_name = sequence_name.replace('|', '_').replace('-', '_').replace('/', '_').replace(':', '_')
    return sequence_name

def generate_output_tables(args, rename_sequence):
    print(f"\n\033[1m{step_counter.print_main_step()}: Generating the merge geNomad and CheckV output tables...\033[0m")
    # Search for files ending with '_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv'
    unfiltered_quality_summary_files = []
    unfiltered_quality_summary_file_pattern = os.path.join(args["input"], '02_CHECK_V', '*', '*_Unfiltered_Merged_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv')
    unfiltered_quality_summary_files.extend(glob.glob(unfiltered_quality_summary_file_pattern))

    # Initialize an empty DataFrame to store the concatenated data
    unfiltered_quality_summary_concatenated_df = pd.DataFrame()

    # Loop through each quality summary file and concatenate the data
    for unfiltered_quality_summary_file in unfiltered_quality_summary_files:
        unfiltered_quality_summary_df = pd.read_csv(unfiltered_quality_summary_file, sep='\t')
        unfiltered_quality_summary_concatenated_df = pd.concat([unfiltered_quality_summary_concatenated_df, unfiltered_quality_summary_df], ignore_index=True)

    # Save the quality_summary_concatenated_df DataFrame to a new file
    unfiltered_quality_summary_concatenated_path = os.path.join(args["input"], '03_CLUSTERING', 'MVP_03_All_Sample_Unfiltered_Merged_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv')
    unfiltered_quality_summary_concatenated_df['virus_id'] = unfiltered_quality_summary_concatenated_df['virus_id'].apply(rename_sequence)
    unfiltered_quality_summary_concatenated_df.to_csv(unfiltered_quality_summary_concatenated_path, sep='\t', index=False)

    # Search for files ending with '_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv'
    filtered_quality_summary_files = []
    filtered_quality_summary_file_pattern = os.path.join(args["input"], '02_CHECK_V', '*', '*_Filtered_Relaxed_Merged_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv')
    filtered_quality_summary_files.extend(glob.glob(filtered_quality_summary_file_pattern))

    # Initialize an empty DataFrame to store the concatenated data
    filtered_quality_summary_concatenated_df = pd.DataFrame()

    # Loop through each quality summary file and concatenate the data
    for filtered_quality_summary_file in filtered_quality_summary_files:
        filtered_quality_summary_df = pd.read_csv(filtered_quality_summary_file, sep='\t')
        filtered_quality_summary_concatenated_df = pd.concat([filtered_quality_summary_concatenated_df, filtered_quality_summary_df], ignore_index=True)

    # Save the quality_summary_concatenated_df DataFrame to a new file
    filtered_quality_summary_concatenated_path = os.path.join(args["input"], '03_CLUSTERING', 'MVP_03_All_Sample_Filtered_Relaxed_Merged_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv')
    filtered_quality_summary_concatenated_df.to_csv(filtered_quality_summary_concatenated_path, sep='\t', index=False)

    return unfiltered_quality_summary_concatenated_df, filtered_quality_summary_concatenated_df

def clustering(args, filtered_quality_summary_concatenated_df):
    print(f"\n\033[1m{step_counter.print_sub_step()}: Concatenating all FASTA sequence files...\033[0m")
    # Get a list of all input FASTA files within the specified directories
    filtered_sequence_files = []
    filtered_sequence_file_pattern = os.path.join(args["input"], '02_CHECK_V', '*', '*_Filtered_Relaxed_Virus_Provirus_Sequences.fna')
    filtered_sequence_files.extend(glob.glob(filtered_sequence_file_pattern, recursive=True))

    # Concatenate the input FASTA files
    output_file = os.path.join(args["input"], '03_CLUSTERING', 'MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences.fna')
    with open(output_file, 'w') as outfile:
        for fasta_file in filtered_sequence_files:
            with open(fasta_file, 'r') as infile:
                outfile.write(infile.read())

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to 03_anicalc.py and 03_aniclust.py
    anicalc_path = os.path.join(script_dir, '03_anicalc.py')
    aniclust_path = os.path.join(script_dir, '03_aniclust.py')

    print(f"\n\033[1m{step_counter.print_sub_step()}: Running makeblastdb on the concatenated FASTA file...\033[0m")
    blastdb_output = os.path.join(args["input"], '03_CLUSTERING', 'MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences_BLAST_DB')
    subprocess.run(['makeblastdb', '-in', output_file, '-dbtype', 'nucl', '-out', blastdb_output])

    print(f"\n\033[1m{step_counter.print_sub_step()}: Running blastn on the concatenated FASTA file...\033[0m")
    blastn_output = os.path.join(args["input"], '03_CLUSTERING', 'MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences_Clustering.tsv')
    subprocess.run(['blastn', '-query', output_file, '-db', blastdb_output, '-outfmt', '6 std qlen slen', '-max_target_seqs', '10000', '-out', blastn_output, '-num_threads', str(args["threads"])])

    print(f"\n\033[1m{step_counter.print_sub_step()}: Creating the clustering output table containing the Representative sequences...\033[0m")
    # Run anicalc.py on the blastn output
    ani_output = os.path.join(args["input"], '03_CLUSTERING', 'MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences_Clustering_ANI.tsv')
    subprocess.run(['python', anicalc_path, '-i', blastn_output, '-o', ani_output])

    # Run aniclust.py on the anicalc.py output
    cluster_output = os.path.join(args["input"], '03_CLUSTERING', 'MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences_Clustering_ANI_Clusters.tsv')
    subprocess.run(['python', aniclust_path, '--fna', output_file, '--ani', ani_output, '--out', cluster_output, '--min_ani', str(args["min_ani"]), '--min_tcov', str(args["min_tcov"]), '--min_qcov', str(args["min_qcov"])])

    # Add column names to the output file
    df = pd.read_csv(cluster_output, sep='\t', header=None)
    df.columns = ['Representative_Sequence', 'Sequences']
    contig_ids_to_keep = set(df['Representative_Sequence'].tolist())
    df.to_csv(cluster_output, sep='\t', index=False)

    representative_filtered_quality_summary_concatenated_df = pd.merge(df, filtered_quality_summary_concatenated_df, left_on='Representative_Sequence',right_on='virus_id', how='left')
    columns_to_exclude = ['virus_id']  # Specify the columns to exclude
    representative_filtered_quality_summary_concatenated_df = representative_filtered_quality_summary_concatenated_df.drop(columns=columns_to_exclude)

    # Save the merged DataFrame to a new file
    representative_filtered_quality_summary_concatenated_path = os.path.join(args["input"], '03_CLUSTERING', 'MVP_03_All_Sample_Filtered_Relaxed_Merged_Genomad_CheckV_Representative_Virus_Proviruses_Quality_Summary.tsv')
    representative_filtered_quality_summary_concatenated_df.to_csv(representative_filtered_quality_summary_concatenated_path, sep='\t', index=False)

    return output_file, contig_ids_to_keep, blastn_output, ani_output, cluster_output, representative_filtered_quality_summary_concatenated_df

def create_representative_fasta_file(args, output_file, contig_ids_to_keep):
    print(f"\n\033[1m{step_counter.print_main_step()}: Creating the FASTA file containing the representative sequences from the clustering step...\033[0m")
    # Find the directory containing the viruses and proviruses fasta files for this sample
    output_file = os.path.join(args["input"], '03_CLUSTERING', 'MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences.fna')

    # Read all lines from the concatenated file
    fasta_lines = []
    with open(output_file, 'r') as f:
        fasta_lines = f.readlines()

    # Filter the concatenated file
    representative_fasta_file = os.path.join(args["input"], '03_CLUSTERING', 'MVP_03_All_Sample_Filtered_Relaxed_Representative_Virus_Provirus_Sequences.fna')
    with open(representative_fasta_file, 'w') as f:
        write_line = False
        for line in fasta_lines:
            if line.startswith('>'):
                contig_id = line.strip()[1:]
                if contig_id in contig_ids_to_keep:
                    write_line = True
                    f.write(line)
                else:
                    write_line = False
            else:
                if write_line:
                    f.write(line)

    return representative_fasta_file

def clean_folder(args, blastn_output, ani_output, cluster_output):
    print(f"\n\033[1m{step_counter.print_main_step()}: Cleaning 03_CLUSTERING directory by removing intermediary files...\033[0m")
    # Create 'tmp' folder
    tmp_folder = os.path.join(args["input"], '03_CLUSTERING', 'tmp')

    # Delete the existing 'tmp' folder if it exists
    if os.path.exists(tmp_folder):
        shutil.rmtree(tmp_folder)

    # Create a new 'tmp' folder
    os.makedirs(tmp_folder, exist_ok=True)

    # Define the source directory and file pattern
    source_directory = os.path.join(args["input"], '03_CLUSTERING')
    file_pattern = 'MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences_BLAST_DB.*'

    # Use glob to find all matching files
    matching_files = glob.glob(os.path.join(source_directory, file_pattern))

    # Move matching files to the temporary folder
    for file_path in matching_files:
        shutil.move(file_path, tmp_folder)

    # Move other files to the temporary folder
    shutil.move(blastn_output, tmp_folder)
    shutil.move(ani_output, tmp_folder)
    shutil.move(cluster_output, tmp_folder)

def generate_index(args, representative_fasta_file):
    print(f"\n\033[1m{step_counter.print_main_step()}: Creating the reference index from the FASTA file containing the representative sequences for Module 04 (Read mapping)...\033[0m")
    # Find path for '04_READ_MAPPING'
    read_mapping_dir = os.path.join(args["input"], '04_READ_MAPPING')

    # If args.read_type is "short" or not provided, create a Bowtie2 index if it does not exist
    reference_path = os.path.join(read_mapping_dir, 'reference')

    if args["read_type"] == 'short' or not args["read_type"]:
        if not os.path.exists(reference_path + '.1.bt2'):
            print("\nRun bowtie2-build: use representative viral sequences to build bowtie database.\n")
            subprocess.run(['bowtie2-build', representative_fasta_file, reference_path])
        else:
            print(f"\nReference index 'reference' already exists in {read_mapping_dir}")
    else:
        # If args.read_type is "long," apply minimap2 to create an index (assuming minimap2 is in your PATH)
        if not os.path.exists(reference_path + '.mmi'):
            print("\nRun minimap2 to create an index from representative viral sequences.\n")
            subprocess.run(['minimap2', '-d', reference_path, representative_fasta_file])
        else:
            print(f"\nReference index 'reference' already exists in {read_mapping_dir}")


def generate_protein_files(args, metadata, output_file, representative_fasta_file):
    functional_annotation_directory = os.path.join(args["input"], '06_FUNCTIONAL_ANNOTATION')
    os.makedirs(functional_annotation_directory, exist_ok=True)

    # Create a dictionary to store sequences by sample_name
    sequences_by_sample = {}

    # Iterate over rows in the metadata DataFrame
    for row_index, (_, row) in enumerate(metadata.iterrows(), start=1):
        sample_name = row['Sample']
        # Construct the path to the provirus protein file based on the sample name
        provirus_protein_file = os.path.join(args["input"], '01_GENOMAD', str(sample_name), f'{sample_name}_Proviruses_Genomad_Output', 'proviruses_summary', 'proviruses_virus_proteins.faa')
        checkv_results = os.path.join(args["input"], '02_CHECK_V', str(sample_name), f'{sample_name}_Viruses_CheckV_Output', 'quality_summary.tsv')
        virus_protein_files = glob.glob(os.path.join(args["input"], '01_GENOMAD', str(sample_name), f'{sample_name}_Viruses_Genomad_Output', f'*_summary', f'*_virus_proteins.faa'))
        checkv_df_proviruses = pd.read_csv(checkv_results, sep='\t')
        list_proviruses = checkv_df_proviruses.loc[checkv_df_proviruses["provirus"] == "Yes"]['contig_id'].to_list()

        # Check if the provirus protein file exists
        if os.path.exists(provirus_protein_file):

            # Load sequences from the provirus protein file
            provirus_sequences = SeqIO.to_dict(SeqIO.parse(provirus_protein_file, "fasta"))

            # Initialize a list to store sequences from virus_protein_files that are not similar to provirus_sequences
            non_similar_sequences = []

            # Iterate over virus protein files
            for virus_protein_file in virus_protein_files:
                # Load sequences from the virus protein file
                virus_sequences = SeqIO.to_dict(SeqIO.parse(virus_protein_file, "fasta"))

                # Find sequences from virus_sequences that are not similar to any sequences in provirus_sequences
                for seq_id, seq_record in virus_sequences.items():
                    contig_id = "_".join(seq_id.split("_")[0:-1])
                    if contig_id not in list_proviruses:
                        non_similar_sequences.append(seq_record)

            # Store the combined sequences from provirus_protein_file and non_similar_sequences
            combined_sequences = list(provirus_sequences.values()) + non_similar_sequences
            sequences_by_sample[sample_name] = combined_sequences
        else:
            # If provirus protein file is missing, use virus protein files as is
            combined_sequences = []
            for virus_protein_file in virus_protein_files:
                combined_sequences.extend(SeqIO.parse(virus_protein_file, "fasta"))
            sequences_by_sample[sample_name] = combined_sequences

    if args["unfiltered_protein_file"]:
        print(f"\n\033[1m{step_counter.print_sub_step()}: Generating FASTA file containing protein sequences from unfiltered viruses...\033[0m")
        # Concatenate all sequences for each sample into a single file
        protein_file = os.path.join(args["input"], '06_FUNCTIONAL_ANNOTATION', "MVP_06_All_Sample_Unfiltered_Virus_Provirus_Protein_Sequences.faa")
        with open(protein_file, "w") as output_handle:
            for sample_name, sequences in sequences_by_sample.items():
                for seq_record in sequences:
                    # Rename the sequence header
                    seq_record.id = rename_protein_sequence(seq_record.id)
                    SeqIO.write(seq_record, output_handle, "fasta")

        return protein_file


    print(f"\n\033[1m{step_counter.print_sub_step()}: Generating FASTA file containing protein sequences from filtered (relaxed mode) viruses...\033[0m")
    # Load the headers from the representative fasta file into a set for faster lookup
    filtered_headers = set(SeqIO.to_dict(SeqIO.parse(output_file, "fasta")).keys())
    filtered_protein_file = os.path.join(args["input"], '06_FUNCTIONAL_ANNOTATION', "MVP_06_All_Sample_Filtered_Relaxed_Virus_Provirus_Protein_Sequences.faa")

    # Concatenate all sequences for each sample into a single file
    with open(filtered_protein_file, "w") as output_handle:
        for sample_name, sequences in sequences_by_sample.items():
            for seq_record in sequences:
                # Rename the sequence header
                seq_record.id = rename_protein_sequence(seq_record.id)
                # Check if the header is in the representative_headers set
                if any(substring in seq_record.id for substring in filtered_headers):
                    SeqIO.write(seq_record, output_handle, "fasta")

    
    # Load the headers from the representative fasta file into a set for faster lookup
    representative_headers = set(SeqIO.to_dict(SeqIO.parse(representative_fasta_file, "fasta")).keys())
    representative_protein_file = os.path.join(args["input"], '06_FUNCTIONAL_ANNOTATION', "MVP_06_All_Sample_Filtered_Relaxed_Representative_Virus_Provirus_Protein_Sequences.faa")

    print(f"\n\033[1m{step_counter.print_sub_step()}: Generating FASTA file containing protein sequences from filtered (relaxed mode) representative vOTUs...\033[0m")
    with open(representative_protein_file, "w") as output_handle:
        for sample_name, sequences in sequences_by_sample.items():
            for seq_record in sequences:
                # Rename the sequence header
                seq_record.id = rename_protein_sequence(seq_record.id)
                # Check if the header is in the representative_headers set
                if any(substring in seq_record.id for substring in representative_headers):
                    SeqIO.write(seq_record, output_handle, "fasta")


# Define a custom sorting key function
def custom_sort_key(gene):
    # Split the viral_gene_id into parts using "_"
    parts = gene.split('_')
    Contig_name = '_'.join(parts[:-1])  # Join all parts except the last one to get Contig_name
    gene_number = int(parts[-1]) if len(parts) > 1 else 0  # Extract the last part as Gene_number

    return Contig_name, gene_number

def generate_genomad_annotation_tables(args, protein_file, filtered_quality_summary_concatenated_df, representative_filtered_quality_summary_concatenated_df):
    # Get a list of all input gene annotation TSV file files within the specified directories
    gene_annotation_files = []
    gene_annotation_file_pattern = os.path.join(args["input"], '01_GENOMAD', '*', '*_Genomad_Output', '*_summary', '*_virus_genes.tsv')
    gene_annotation_files.extend(glob.glob(gene_annotation_file_pattern, recursive=True))
    
    # Concatenate all DataFrames into a single DataFrame
    dfs = []
    for file in gene_annotation_files:
        df = pd.read_csv(file, sep='\t', usecols=['gene', 'start', 'end', 'length', 'strand', 'gc_content', 'genetic_code', 'rbs_motif', 'marker', 'evalue', 
                                                'bitscore', 'virus_hallmark', 'annotation_amr', 'annotation_accessions',
                                                'annotation_description'])
        dfs.append(df)

    concatenated_gene_annotation_files = pd.concat(dfs, ignore_index=True)
    concatenated_gene_annotation_files['gene'] = concatenated_gene_annotation_files['gene'].apply(rename_protein_sequence_table)

    # Sort rows by Contig_name and Gene_number using the custom sorting key
    concatenated_gene_annotation_files[['Contig_name', 'Gene_number']] = concatenated_gene_annotation_files['gene'].apply(custom_sort_key).apply(pd.Series)
    concatenated_gene_annotation_files.insert(1, 'Contig_name', concatenated_gene_annotation_files.pop('Contig_name'))
    concatenated_gene_annotation_files.insert(2, 'Gene_number', concatenated_gene_annotation_files.pop('Gene_number'))

    if args["unfiltered_protein_file"]:
        print(f"\n\033[1m{step_counter.print_sub_step()}: Generating geNomad function annotation table containing unfiltered viral contigs...\033[0m")
        concatenated_gene_annotation_files_path = os.path.join(args["input"], '06_FUNCTIONAL_ANNOTATION', "MVP_06_All_Sample_Unfiltered_Merged_Genomad_CheckV_Virus_Proviruses_Gene_Annotation_GENOMAD.tsv")
        protein_file_headers = set(SeqIO.to_dict(SeqIO.parse(protein_file, "fasta")).keys())
        concatenated_gene_annotation_files = concatenated_gene_annotation_files[concatenated_gene_annotation_files['gene'].isin(protein_file_headers)]
        concatenated_gene_annotation_files.to_csv(concatenated_gene_annotation_files_path, sep ='\t')


    print(f"\n\033[1m{step_counter.print_sub_step()}: Generating geNomad function annotation table containing filtered (relaxed mode) viral contigs...\033[0m")
    merged_concatenated_gene_annotation_files = pd.merge(filtered_quality_summary_concatenated_df[['virus_id']], concatenated_gene_annotation_files, left_on='virus_id',right_on='Contig_name', how='left')

    merged_concatenated_gene_annotation_files = merged_concatenated_gene_annotation_files.sort_values(by=['Contig_name', 'Gene_number'], ascending=[True, True])
    columns_to_fill_unknown = ['annotation_amr', 'annotation_accessions', 'annotation_description']
    merged_concatenated_gene_annotation_files[columns_to_fill_unknown] = merged_concatenated_gene_annotation_files[columns_to_fill_unknown].fillna('Unknown')
    merged_concatenated_gene_annotation_files.fillna('NA', inplace=True)
    merged_concatenated_gene_annotation_files.drop(columns=['virus_id'], inplace=True)
    merged_concatenated_gene_annotation_files.rename(columns={'gene': 'Viral_gene_ID'}, inplace=True)
    merged_concatenated_gene_annotation_files['virus_hallmark'] = merged_concatenated_gene_annotation_files['virus_hallmark'].replace({0: 'NA', 1: 'Virus_hallmark'})
    desired_column_order = ['Viral_gene_ID', 'Contig_name', 'Gene_number', 'start', 'end', 'length', 'strand', 'annotation_description', 'annotation_accessions', 'bitscore', 'evalue', 'gc_content', 'genetic_code', 'rbs_motif',
        'marker', 'virus_hallmark', 'annotation_amr']
    merged_concatenated_gene_annotation_files = merged_concatenated_gene_annotation_files[desired_column_order]
    new_column_names = {'gc_content': 'GENOMAD_gc_content', 'genetic_code': 'GENOMAD_genetic_code', 'rbs_motif': 'GENOMAD_rbs_motif', 'marker': 'GENOMAD_marker', 'evalue': 'GENOMAD_evalue',
        'bitscore': 'GENOMAD_Score',  'virus_hallmark': 'GENOMAD_virus_hallmark', 'annotation_amr': 'GENOMAD_Annotation_amr', 'annotation_accessions': 'GENOMAD_Annotation_accessions',
        'annotation_description': 'GENOMAD_Annotation'}
    merged_concatenated_gene_annotation_files.rename(columns=new_column_names, inplace=True)
    merged_concatenated_gene_annotation_files_path = os.path.join(args["input"], '06_FUNCTIONAL_ANNOTATION', "MVP_06_All_Sample_Filtered_Relaxed_Merged_Genomad_CheckV_Virus_Proviruses_Gene_Annotation_GENOMAD.tsv")
    merged_concatenated_gene_annotation_files.to_csv(merged_concatenated_gene_annotation_files_path, sep ='\t')

    print(f"\n\033[1m{step_counter.print_sub_step()}: Generating geNomad function annotation table containing filtered (relaxed mode) representative vOTUs...\033[0m")
    representative_merged_concatenated_gene_annotation_files = pd.merge(representative_filtered_quality_summary_concatenated_df[['Representative_Sequence']], merged_concatenated_gene_annotation_files, left_on='Representative_Sequence',right_on='Contig_name', how='left')
    representative_merged_concatenated_gene_annotation_files.drop(columns=['Representative_Sequence'], inplace=True)
    representative_merged_concatenated_gene_annotation_files_path = os.path.join(args["input"], '06_FUNCTIONAL_ANNOTATION', "MVP_06_All_Sample_Filtered_Relaxed_Merged_Genomad_CheckV_Representative_Virus_Proviruses_Gene_Annotation_GENOMAD.tsv")
    representative_merged_concatenated_gene_annotation_files.to_csv(representative_merged_concatenated_gene_annotation_files_path, sep ='\t')


def generate_summary_report(args, unfiltered_quality_summary_concatenated_df, filtered_quality_summary_concatenated_df, representative_filtered_quality_summary_concatenated_df, mvp_formatted_start_time, mvp_formatted_end_time, mvp_duration):
    print(f"\n\033[1m{step_counter.print_main_step()}: Creating the summary report for Module 03 (Clustering)...\033[0m")
    # Calculate summary statistics before both filtration and clustering 
    num_unfiltered_viruses = len(unfiltered_quality_summary_concatenated_df)
    num_unfiltered_proviruses = (unfiltered_quality_summary_concatenated_df['provirus'].str.contains('Yes', case=False)).sum()
    mean_unfiltered_virus_length = unfiltered_quality_summary_concatenated_df['virus_length'].mean()
    max_unfiltered_virus_length = unfiltered_quality_summary_concatenated_df['virus_length'].max()
    min_unfiltered_virus_length = unfiltered_quality_summary_concatenated_df['virus_length'].min()
    unfiltered_virus_quality_counts = unfiltered_quality_summary_concatenated_df['checkv_quality'].value_counts()

    # Count occurrences of each realm in the second level of the taxonomy column
    unfiltered_virus_taxa_levels = unfiltered_quality_summary_concatenated_df['taxonomy'].str.split(';')
    unfiltered_virus_second_level_taxa = unfiltered_virus_taxa_levels.apply(lambda x: x[1] if len(x) > 1 else 'Unclassified/others')
    unfiltered_virus_taxa_counts = unfiltered_virus_second_level_taxa.value_counts()
    # Calculate the percentage of each realm
    unfiltered_virus_taxa_percentages = (unfiltered_virus_taxa_counts / num_unfiltered_viruses) * 100
    # Prepare the summary report content
    unfiltered_virus_taxa_summary = "\n".join([f"{realm}: {count} ({percentage:.1f}%)" for realm, count, percentage in zip(unfiltered_virus_taxa_counts.index, unfiltered_virus_taxa_counts.values, unfiltered_virus_taxa_percentages.values)])

    # Prepare the summary report content for top classes
    unfiltered_virus_taxa_levels = unfiltered_quality_summary_concatenated_df['taxonomy'].str.split(';').apply(lambda levels: levels + [''] * (5 - len(levels)))
    unfiltered_virus_fifth_level_classes = unfiltered_virus_taxa_levels.apply(lambda x: x[4])
    unfiltered_virus_filtered_classes = unfiltered_virus_fifth_level_classes[(unfiltered_virus_fifth_level_classes != '') & (unfiltered_virus_fifth_level_classes != 'Unclassified')]
    unfiltered_virus_class_counts = unfiltered_virus_filtered_classes.value_counts()
    unfiltered_virus_top_10_classes = unfiltered_virus_class_counts.nlargest(10)
    unfiltered_virus_top_classes_summary = "\n".join([f"{cls}: {count}" for cls, count in unfiltered_virus_top_10_classes.items()])

    # Calculate summary statistics after filtration and before clustering
    num_filtered_virus = len(filtered_quality_summary_concatenated_df)
    num_filtered_provirus = (filtered_quality_summary_concatenated_df['provirus'].str.contains('Yes', case=False)).sum()
    mean_filtered_virus_length = filtered_quality_summary_concatenated_df['virus_length'].mean()
    max_filtered_virus_length = filtered_quality_summary_concatenated_df['virus_length'].max()
    min_filtered_virus_length = filtered_quality_summary_concatenated_df['virus_length'].min()
    filtered_virus_quality_counts = filtered_quality_summary_concatenated_df['checkv_quality'].value_counts()

    # Count occurrences of each realm in the second level of the taxonomy column
    filtered_virus_taxa_levels = filtered_quality_summary_concatenated_df['taxonomy'].str.split(';')
    filtered_virus_second_level_taxa = filtered_virus_taxa_levels.apply(lambda x: x[1] if len(x) > 1 else 'Unclassified/others')
    filtered_virus_taxa_counts = filtered_virus_second_level_taxa.value_counts()
    # Calculate the percentage of each realm
    filtered_virus_taxa_percentages = (filtered_virus_taxa_counts / num_filtered_virus) * 100
    # Prepare the summary report content
    filtered_virus_taxa_summary = "\n".join([f"{realm}: {count} ({percentage:.1f}%)" for realm, count, percentage in zip(filtered_virus_taxa_counts.index, filtered_virus_taxa_counts.values, filtered_virus_taxa_percentages.values)])

    # Prepare the summary report content for top classes
    filtered_virus_taxa_levels = filtered_quality_summary_concatenated_df['taxonomy'].str.split(';').apply(lambda levels: levels + [''] * (5 - len(levels)))
    filtered_virus_fifth_level_classes = filtered_virus_taxa_levels.apply(lambda x: x[4])
    filtered_virus_filtered_classes = filtered_virus_fifth_level_classes[(filtered_virus_fifth_level_classes != '') & (filtered_virus_fifth_level_classes != 'Unclassified')]
    filtered_virus_class_counts = filtered_virus_filtered_classes.value_counts()
    filtered_virus_top_10_classes = filtered_virus_class_counts.nlargest(10)
    filtered_virus_top_classes_summary = "\n".join([f"{cls}: {count}" for cls, count in filtered_virus_top_10_classes.items()])

    # Calculate summary statistics after both filtration and clustering
    num_vOTUs = len(representative_filtered_quality_summary_concatenated_df)
    num_provOTUs = (representative_filtered_quality_summary_concatenated_df['provirus'].str.contains('Yes', case=False)).sum()
    mean_vOTUs_length = representative_filtered_quality_summary_concatenated_df['virus_length'].mean()
    max_vOTUs_length = representative_filtered_quality_summary_concatenated_df['virus_length'].max()
    min_vOTUs_length = representative_filtered_quality_summary_concatenated_df['virus_length'].min()
    vOTUs_quality_counts = representative_filtered_quality_summary_concatenated_df['checkv_quality'].value_counts()

    # Count occurrences of each realm in the second level of the taxonomy column
    vOTUs_taxa_levels = representative_filtered_quality_summary_concatenated_df['taxonomy'].str.split(';')
    vOTUs_second_level_taxa = vOTUs_taxa_levels.apply(lambda x: x[1] if len(x) > 1 else 'Unclassified/others')
    vOTUs_taxa_counts = vOTUs_second_level_taxa.value_counts()
    # Calculate the percentage of each realm
    vOTUs_taxa_percentages = (vOTUs_taxa_counts / num_vOTUs) * 100
    # Prepare the summary report content
    vOTUs_taxa_summary = "\n".join([f"{realm}: {count} ({percentage:.1f}%)" for realm, count, percentage in zip(vOTUs_taxa_counts.index, vOTUs_taxa_counts.values, vOTUs_taxa_percentages.values)])

    # Prepare the summary report content for top classes
    vOTUs_taxa_levels = representative_filtered_quality_summary_concatenated_df['taxonomy'].str.split(';').apply(lambda levels: levels + [''] * (5 - len(levels)))
    vOTUs_fifth_level_classes = vOTUs_taxa_levels.apply(lambda x: x[4])
    vOTUs_filtered_classes = vOTUs_fifth_level_classes[(vOTUs_fifth_level_classes != '') & (vOTUs_fifth_level_classes != 'Unclassified')]
    vOTUs_class_counts = vOTUs_filtered_classes.value_counts()
    vOTUs_top_10_classes = vOTUs_class_counts.nlargest(10)
    vOTUs_top_classes_summary = "\n".join([f"{cls}: {count}" for cls, count in vOTUs_top_10_classes.items()])

    # Define the path for the new summary report for Module 03
    summary_report_path_module_03 = os.path.join(args["input"], '03_CLUSTERING', 'MVP_03_Summary_Report.txt')

    # Create a dictionary to hold argument descriptions and their default values
    argument_defaults = {
        '--input': args["input"],
        '--metadata': args["metadata"],
        '--min_ani': args["min_ani"],
        '--min_tcov': args["min_tcov"],
        '--min_qcov': args["min_qcov"],
        '--threads': args["threads"]}

    # Write a summary line with script arguments and their default values
    summary_line = "03_do_clustering.py"
    for arg, default in argument_defaults.items():
        if default is not None:
            summary_line += f" {arg} {default}"

    start_time = f"\nStart Time: {mvp_formatted_start_time}\n"
    end_time = f"End time: {mvp_formatted_end_time}\n"
    duration = f"Running Time: {mvp_duration.total_seconds():.2f} seconds\n"

    # Prepare the content for Module 03 summary report
    module_03_summary_content = f"""****************************************************************************
******************               MODULE 03                ******************
****************************************************************************

{summary_line}
{start_time}
{end_time}
{duration}

Summary Report before both filtration and clustering 
--------------------------
Number of Viruses: {num_unfiltered_viruses}, including {num_unfiltered_proviruses} proviruses
Mean Length: {mean_unfiltered_virus_length:.2f}
Max Length: {max_unfiltered_virus_length}
Min Length: {min_unfiltered_virus_length}

Unfiltered Viruses CheckV quality summary:
Low Quality: {unfiltered_virus_quality_counts.get('Low-quality', 0)}
Medium Quality: {unfiltered_virus_quality_counts.get('Medium-quality', 0)}
High Quality: {unfiltered_virus_quality_counts.get('High-quality', 0)}
Complete: {unfiltered_virus_quality_counts.get('Complete', 0)}
Not determined: {unfiltered_virus_quality_counts.get('Not-determined', 0)}

Unfiltered Viruses taxonomy summary:
{unfiltered_virus_taxa_summary}

Top 10 classes of Unfiltered Viruses:
{unfiltered_virus_top_classes_summary}

Summary Report after filtration and before clustering
--------------------------
Number of Viruses: {num_filtered_virus}, including {num_filtered_provirus} proviruses
Mean Length: {mean_filtered_virus_length:.2f}
Max Length: {max_filtered_virus_length}
Min Length: {min_filtered_virus_length}

Filtered Viruses CheckV quality summary:
Low Quality: {filtered_virus_quality_counts.get('Low-quality', 0)}
Medium Quality: {filtered_virus_quality_counts.get('Medium-quality', 0)}
High Quality: {filtered_virus_quality_counts.get('High-quality', 0)}
Complete: {filtered_virus_quality_counts.get('Complete', 0)}
Not determined: {filtered_virus_quality_counts.get('Not-determined', 0)}

Filtered Viruses taxonomy summary:
{filtered_virus_taxa_summary}

Top 10 classes of Filtered Viruses:
{filtered_virus_top_classes_summary}

Summary Report after both filtration and clustering
--------------------------
Number of vOTUs: {num_vOTUs}, including {num_provOTUs} proviruses
Mean Length: {mean_vOTUs_length:.2f}
Max Length: {max_vOTUs_length}
Min Length: {min_vOTUs_length}

vOTUs CheckV quality summary:
Low Quality: {vOTUs_quality_counts.get('Low-quality', 0)}
Medium Quality: {vOTUs_quality_counts.get('Medium-quality', 0)}
High Quality: {vOTUs_quality_counts.get('High-quality', 0)}
Complete: {vOTUs_quality_counts.get('Complete', 0)}
Not determined: {vOTUs_quality_counts.get('Not-determined', 0)}

vOTUs taxonomy summary:
{vOTUs_taxa_summary}

Top 10 classes of vOTUs:
{vOTUs_top_classes_summary}

"""

    # Write the content to the new summary report for Module 03
    with open(summary_report_path_module_03, 'w') as module_03_summary_report:
        module_03_summary_report.write(module_03_summary_content)

def main(args):
    # Capture start time
    mvp_start_time = datetime.datetime.now()
    mvp_formatted_start_time = mvp_start_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nStart Time: {mvp_formatted_start_time}") 

    # read metadata file and map FASTQ files
    metadata = pd.read_csv(args["metadata"], sep='\t')

    unfiltered_quality_summary_concatenated_df, filtered_quality_summary_concatenated_df = generate_output_tables(args, rename_sequence)

    output_file, contig_ids_to_keep, blastn_output, ani_output, cluster_output, representative_filtered_quality_summary_concatenated_df = clustering(args, filtered_quality_summary_concatenated_df)

    representative_fasta_file = create_representative_fasta_file(args, output_file, contig_ids_to_keep)

    clean_folder(args, blastn_output, ani_output, cluster_output)

    generate_index(args, representative_fasta_file)
    
    protein_file = generate_protein_files(args, metadata, output_file, representative_fasta_file)

    generate_genomad_annotation_tables(args, protein_file, filtered_quality_summary_concatenated_df, representative_filtered_quality_summary_concatenated_df)

    # Capture end time
    mvp_end_time = datetime.datetime.now()
    mvp_formatted_end_time = mvp_end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate duration
    mvp_duration = mvp_end_time - mvp_start_time

    generate_summary_report(args, unfiltered_quality_summary_concatenated_df, filtered_quality_summary_concatenated_df, representative_filtered_quality_summary_concatenated_df, mvp_formatted_start_time, mvp_formatted_end_time, mvp_duration)

    message1 = f"\n\033[1mModule 03 finished: virus genome clustering based on pairwise {args['min_ani']}% ANI done!\033[0m"
    message2 = f"Output files (clustering TXT files and sequence FASTA files) saved in {args['input']}/03_CLUSTERING directory."
    message3 = f"MVP_03_summary_report.txt saved in {args['input']}03_CLUSTERING."
    message4 = f"Reference database from representative viral sequence FASTA file has been generated in {args['input']}/04_READ_MAPPING.\n"
    message4 = f"Representative viral sequence FASTA file and reference will be used as inputs for Module 04 (read mapping)."
    message5 = f"Viral protein FASTA files has been generated in {args['input']}/06_FUNCTIONAL_ANNOTATION directory and will be used as inputs for Module 06 (functional annotation)."
    message6 = "\n\033[1mYou can now proceed to the next step of the MVP script: Module 04!\033[0m\n"
    line_of_stars = '*' * len(message2)
    print()
    print(line_of_stars)
    print(message1)
    print(f"\nStart Time: {mvp_formatted_start_time}") 
    print(f"nd Time: {mvp_formatted_end_time}")
    print(f"Running Time: {mvp_duration.total_seconds():.2f} seconds\n")
    print(message2)
    print(message3)
    print(message4)
    print(message5)
    print(message6)
    print(line_of_stars)
    print()

    print("Please don't forget to cite MVP and the following software used by this module:")
    print("- Nayfach, S., Camargo, A.P., Schulz, F. et al. CheckV assesses the quality and completeness of metagenome-assembled viral genomes. Nat Biotechnol 39, 578–585 (2021). https://doi.org/10.1038/s41587-020-00774-7\n")
    print("- Langmead B, Salzberg S. Fast gapped-read alignment with Bowtie 2. Nature Methods. 2012, 9:357-359\n")
    print("- Li H. New strategies to improve minimap2 alignment accuracy. Bioinformatics. 2021, 37(23):4572–4574. https://academic.oup.com/bioinformatics/article/37/23/4572/6384570?login=true\n")