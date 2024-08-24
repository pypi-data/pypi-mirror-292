import os
import argparse
import subprocess
import pandas as pd
import shutil
import csv
from Bio import SeqIO
import re
import datetime
import time
import mvip

def fetch_arguments(parser):
    parser.set_defaults(func=main)
    parser.set_defaults(program="MVP_06_do_functional_annotation")
    parser.add_argument(
        "--input", "-i",
        help="Path to your working directory where you want to run MVP.",
    )
    parser.add_argument(
        "--metadata", "-m",
        help="Path to your metadata that you want to use to run MVP.",
    )
    parser.add_argument('--fasta_files', 
        type=str, 
        default='representative', 
        choices=['representative', 'all'], 
        help='Sequence and protein FASTA files (representative or all sequences) to use for functional annotation. Default = representative',
    )
    parser.add_argument('--delete_files', 
        action='store_true', 
        help='flag to delete unwanted files',
    )
    parser.add_argument('--PHROGS_evalue', 
        type=int, 
        default=0.01, 
        help='Significance e-value of match between target sequences and query (default = 0.01)',
    )
    parser.add_argument('--PHROGS_score', 
        type=int, 
        default=50, 
        help='Significant score of match between target sequences and query (default = 50)',
    )
    parser.add_argument('--PFAM_evalue', 
        type=int, 
        default=0.01, 
        help='Significance e-value of match between target sequences and query (default = 0.01)',
    )
    parser.add_argument('--PFAM_score', 
        type=int, 
        default=50, 
        help='Significant score of match between target sequences and query (default = 50)',
    )
    parser.add_argument('--ADS', 
        action='store_true', 
        help='Include this flag to search ADS profiles.',
    )
    parser.add_argument('--ADS_evalue', 
        type=int, 
        default=0.01, 
        help='Significance e-value of match between target sequences and query (default = 0.01)',
    )
    parser.add_argument('--ADS_score', 
        type=int, 
        default=60, 
        help='Significant score of match between target sequences and query (default = 60)',
    )
    parser.add_argument('--RdRP', 
        action='store_true', 
        help='Include this flag to create the 07_RDRP_PHYLOGENY folder and search RdRP profiles.',
    )
    parser.add_argument('--RdRP_evalue', 
        type=int, 
        default=0.001, 
        help='Significance e-value of match between target sequences and query (default = 0.01)',
    )
    parser.add_argument('--RdRP_score', 
        type=int, 
        default=50, 
        help='Significant score of match between target sequences and query (default = 50)',
    )
    parser.add_argument('--DRAM', 
        action='store_true', 
        help='Include this flag to create a file to be process through DRAM-v.',
    )
    parser.add_argument('--force_prodigal', 
        action='store_true', 
        help='Force execution of protein prediction by Prodigal.',
    )
    parser.add_argument('--force_PHROGS', 
        action='store_true', 
        help='Force PHROGS annotation.',
    )
    parser.add_argument('--force_PFAM', 
        action='store_true', 
        help='Force PFAM annotation.',
    )
    parser.add_argument('--force_ADS', 
        action='store_true', 
        help='Force ADS annotation.',
    )
    parser.add_argument('--force_RdRP', 
        action='store_true', 
        help='Force RdRP annotation.',
    )
    parser.add_argument('--force_outputs', 
        action='store_true', 
        help='Force creation of final annotation table even though it exists.',
    )
    parser.add_argument('--threads', 
        type=int, 
        default=1, 
        help='Number of threads to use (default = 1)',
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

def set_up_paths(args):
    # Construct the path to the phrogs file
    script_directory = os.path.dirname(os.path.abspath(__file__))

    if args['fasta_files'] == 'all':
        proteins_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', 'MVP_06_All_Sample_Filtered_Relaxed_Virus_Provirus_Protein_Sequences.faa')
        sequence_file = os.path.join(args['input'], '03_CLUSTERING', 'MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences.fna')
        genomad_annotation = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', 'MVP_06_All_Sample_Filtered_Relaxed_Merged_Genomad_CheckV_Virus_Proviruses_Gene_Annotation_GENOMAD.tsv')
    else:
        proteins_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', 'MVP_06_All_Sample_Filtered_Relaxed_Representative_Virus_Provirus_Protein_Sequences.faa')
        sequence_file = os.path.join(args['input'], '03_CLUSTERING', 'MVP_03_All_Sample_Filtered_Relaxed_Representative_Virus_Provirus_Sequences.fna')
        genomad_annotation = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', 'MVP_06_All_Sample_Filtered_Relaxed_Merged_Genomad_CheckV_Representative_Virus_Proviruses_Gene_Annotation_GENOMAD.tsv')

    if args['RdRP'] and args['ADS']:
        final_annotation_output_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', os.path.splitext(os.path.basename(genomad_annotation))[0] + '_PHROGS_PFAM_ADS_RDRP_Filtered.tsv')
    elif args['RdRP']:
        final_annotation_output_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', os.path.splitext(os.path.basename(genomad_annotation))[0] + '_PHROGS_PFAM_RDRP_Filtered.tsv')
    elif args['ADS']:
        final_annotation_output_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', os.path.splitext(os.path.basename(genomad_annotation))[0] + '_PHROGS_PFAM_ADS_Filtered.tsv')
    else:
        final_annotation_output_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', os.path.splitext(os.path.basename(genomad_annotation))[0] + '_PHROGS_PFAM_Filtered.tsv')

    phrogs_output_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', os.path.basename(genomad_annotation).replace('_GENOMAD.tsv', '_PHROGS.tsv'))
    pfam_output_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', os.path.basename(genomad_annotation).replace('_GENOMAD.tsv', '_PFAM.tsv'))
    hmmscan_ADS_output_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', os.path.basename(genomad_annotation).replace('_GENOMAD.tsv', '_hmmscan_ADS.tsv'))
    diamond_ADS_output_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', os.path.basename(genomad_annotation).replace('_GENOMAD.tsv', '_diamond_ADS.tsv'))
    parsed_hmmscan_ADS_output_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', os.path.basename(genomad_annotation).replace('_GENOMAD.tsv', '_hmmscan_ADS_parsed.tsv'))
    parsed_diamond_ADS_output_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', os.path.basename(genomad_annotation).replace('_GENOMAD.tsv', '_diamond_ADS_parsed.tsv'))
    unfiltered_parsed_ADS_output_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', os.path.basename(genomad_annotation).replace('_GENOMAD.tsv', '_Parsed_ADS.tsv'))
    temp_directory = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', 'tmp')

    return script_directory, proteins_file, sequence_file, final_annotation_output_file, phrogs_output_file, temp_directory, pfam_output_file, genomad_annotation, hmmscan_ADS_output_file, diamond_ADS_output_file, parsed_hmmscan_ADS_output_file, parsed_diamond_ADS_output_file, unfiltered_parsed_ADS_output_file
    
def predict_protein(args, proteins_file, sequence_file):
    # Check if the output proteins file exists
    if not os.path.exists(proteins_file) or args["force_prodigal"]:
        # The file doesn't exist, so run Prodigal to predict proteins
        print(f"\n\033[1m{step_counter.print_main_step()}: Running Prodigal to predict proteins because protein file doesn't exist or --force_prodigal provided...\033[0m")
        subprocess.run(['prodigal', '-i', sequence_file, '-a', proteins_file, '--threads', str(args['threads'])])
    else:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping Prodigal to predict proteins because {proteins_file} already exists...\033[0m")

def generate_target_sequence(proteins_file):
    print(f"\n\033[1m{step_counter.print_main_step()}: Creating a target sequence file as an input for the following functional annotation steps...\033[0m")

    target_sequences = os.path.splitext(proteins_file)[0] + '_target_sequences'
    subprocess.run(['mmseqs', 'createdb', proteins_file, target_sequences])

    return target_sequences

def custom_sort_key(viral_gene_id):
    # Sort rows by Contig_name and Gene_number using the custom sorting key
    parts = viral_gene_id.split('_')
    Contig_name = '_'.join(parts[:-1])
    gene_number = int(parts[-1]) if len(parts) > 1 else 0
    return Contig_name, gene_number

def phrogs_annotation(args, proteins_file, target_sequences,  phrogs_output_file, temp_directory):
    # Load the PHROGS database files
    phrogs_db = os.path.join(args["input"], '00_DATABASES', 'PhrogDB_v14', 'phrogs_prof')
    phrogs_index = os.path.join(args["input"], '00_DATABASES', 'PhrogDB_v14', 'PHROGS_index_filter.csv')

    # Run mmseqs search against PHROGS database
    phrogs = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', os.path.splitext(os.path.basename(proteins_file))[0] + '_mmseqs2_PHROGS')
    if os.path.exists(phrogs_output_file) and not args["force_PHROGS"]:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping PHROGS annotation, {phrogs_output_file} file already exists and --force_PHROGS not provided...\033[0m")
    else:
        if os.path.exists(phrogs) and not args["force_PHROGS"]:
            print(f"\n\033[1m{step_counter.print_sub_step()}: Skipping mmseqs search for {target_sequences}, {phrogs} file already exists and --force_PHROGS not provided......\033[0m")
        else:
            print(f"\n\033[1m{step_counter.print_sub_step()}: Annotating proteins against PHROGS database...\033[0m")
            subprocess.run(['mmseqs', 'search', phrogs_db, target_sequences, phrogs, temp_directory, '-s', '7', '--threads', str(args['threads'])])

        print(f"\n\033[1m{step_counter.print_sub_step()}: Creating PHROGS annotation output table...\033[0m")
        subprocess.run(['mmseqs', 'createtsv', phrogs_db, target_sequences, phrogs, phrogs_output_file, '--threads', str(args['threads'])])

        phrogs_output_file_df = pd.read_csv(phrogs_output_file, sep='\t', encoding_errors='ignore', names=['#phrog', 'Viral_gene_ID', 'PHROGS_Score', 'PHROGS_seqIdentity', 'PHROGS_evalue', 'qStart', 'qEnd', 'qLen', 'tStart', 'tEnd', 'tLen'])
        phrogs_output_file_df['#phrog'] = phrogs_output_file_df['#phrog'].str.replace('.fma', '')
        phrogs_output_file_df[['Contig_name', 'Gene_number']] = phrogs_output_file_df['Viral_gene_ID'].apply(custom_sort_key).apply(pd.Series)
        phrogs_output_file_df.insert(2, 'Contig_name', phrogs_output_file_df.pop('Contig_name'))
        phrogs_output_file_df.insert(3, 'Gene_number', phrogs_output_file_df.pop('Gene_number'))
        phrogs_output_file_df = phrogs_output_file_df.sort_values(by=['Contig_name', 'Gene_number'], ascending=[True, True])

        # Merge phrogs_output_csv_file and phrogs_index based on the '#phrog' column
        phrogs_index_df = pd.read_csv(phrogs_index)
        annotation_phrogs_output_file_df = pd.merge(phrogs_output_file_df, phrogs_index_df, on='#phrog', how='left').fillna('Unknown')
        annotation_phrogs_output_file_df['PHROGS_Category'] = annotation_phrogs_output_file_df['PHROGS_Category'].str.replace(' function', '')
        annotation_phrogs_output_file_df = annotation_phrogs_output_file_df.drop(columns=annotation_phrogs_output_file_df.columns[0])
        annotation_phrogs_output_file_df.to_csv(phrogs_output_file, sep='\t')

def pfam_annotation(args, proteins_file, target_sequences, pfam_output_file, temp_directory):
    # Load the PFAM database files
    pfam_db = os.path.join(args["input"], '00_DATABASES', 'Pfam_A_DB', 'pfam')
    pfam_index = os.path.join(args["input"], '00_DATABASES', 'Pfam_A_DB', 'PFAM_Index.tsv')
    
    # Run mmseqs search against PFAM database
    pfam = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', os.path.splitext(os.path.basename(proteins_file))[0] + '_mmseqs2_PFAM')
    if os.path.exists(pfam_output_file) and not args["force_PFAM"]:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping PFAM annotation, {pfam_output_file} file already exists and --force_PFAM not provided...\033[0m")
    else:
        if os.path.exists(pfam) and not args["force_PFAM"]:
            print(f"\n\033[1m{step_counter.print_sub_step()}: Skipping mmseqs search for {target_sequences}, {pfam} file already exists and --force_PFAM not provided...\033[0m")
        else:
            print(f"\n\033[1m{step_counter.print_sub_step()}: Annotating proteins against Pfam database...\033[0m")
            subprocess.run(['mmseqs', 'search', pfam_db, target_sequences, pfam, temp_directory, '-s', '7', '--threads', str(args['threads'])])

        print(f"\n\033[1m{step_counter.print_sub_step()}: Creating Pfam annotation output table...\033[0m")
        subprocess.run(['mmseqs', 'createtsv', pfam_db, target_sequences, pfam, pfam_output_file, '--threads', str(args['threads'])])

        # Read pfam annotation table to merge it with pfam index
        pfam_output_file_df = pd.read_csv(pfam_output_file, sep='\t', encoding_errors='ignore', names=['PFAM_Accession_Number', 'Viral_gene_ID', 'PFAM_Score', 'PFAM_seqIdentity', 'PFAM_evalue', 'qStart', 'qEnd', 'qLen', 'tStart', 'tEnd', 'tLen'])
        pfam_output_file_df['PFAM_Accession_Number'] = pfam_output_file_df['PFAM_Accession_Number'].str.split('.').str[0]
        pfam_index_df = pd.read_csv(pfam_index, sep='\t', encoding_errors='ignore')
        annotation_pfam_output_file_df = pd.merge(pfam_output_file_df, pfam_index_df, left_on='PFAM_Accession_Number', right_on='#pfam', how='left').fillna('Unknown')
        annotation_pfam_output_file_df.to_csv(pfam_output_file, sep='\t')


def merge_phrogs_pfam_tables(args, phrogs_output_file, genomad_annotation, pfam_output_file):
    # Read PHROGS output file
    annotation_phrogs_output_file_df = pd.read_csv(phrogs_output_file, sep='\t', encoding_errors='ignore', usecols=['Viral_gene_ID', 'PHROGS_Score', 'PHROGS_seqIdentity', 'PHROGS_evalue', 'PHROGS_Annotation',
                                                                                                        'PHROGS_Category', 'PHROGS_RefSeq_Annotation', 'PHROGS_Pfam_Annotation',
                                                                                                        'PHROGS_GO_Annotation', 'PHROGS_KO_Annotation'])
    # Filter PHROGS output based on score and evalue
    filter_annotated_phrogs_output_file_df = annotation_phrogs_output_file_df.loc[(annotation_phrogs_output_file_df['PHROGS_Score'] >= args['PHROGS_score']) & (annotation_phrogs_output_file_df['PHROGS_evalue'] <= args['PHROGS_evalue'])]
    # Sort and drop duplicates based on Viral_gene_ID
    filter_annotated_phrogs_output_file_df = filter_annotated_phrogs_output_file_df.sort_values('PHROGS_Score', ascending=False).drop_duplicates('Viral_gene_ID').sort_index()

    # Read Genomad annotation file
    genomad_annotation_df = pd.read_csv(genomad_annotation, sep='\t')
    # Merge Genomad annotation with filtered PHROGS output
    all_genes_filter_annotated_phrogs_output_file_df = pd.merge(genomad_annotation_df, filter_annotated_phrogs_output_file_df, on='Viral_gene_ID', how='left').fillna('NA')

    # Read PFAM output file
    annotation_pfam_output_file_df = pd.read_csv(pfam_output_file, sep='\t', encoding_errors='ignore', usecols=['Viral_gene_ID', 'PFAM_Accession_Number', 'PFAM_Annotation', 'PFAM_Annotation_Short', 'PFAM_Category', 'PFAM_seqIdentity', "PFAM_Score", "PFAM_evalue"])
    # Filter PFAM output based on score and evalue
    PFAM_Index_Filter_df = annotation_pfam_output_file_df.loc[(annotation_pfam_output_file_df['PFAM_Score'] >= args['PFAM_score']) & (annotation_pfam_output_file_df['PFAM_evalue'] <= args['PFAM_evalue'])]
    # Sort and drop duplicates based on Viral_gene_ID
    PFAM_Index_Filter_df = PFAM_Index_Filter_df.sort_values('PFAM_Score', ascending=False).drop_duplicates('Viral_gene_ID').sort_index()
    # Merge Genomad, PHROGS, and PFAM annotations
    PFAM_GENOMAD_PHROGS_df = pd.merge(all_genes_filter_annotated_phrogs_output_file_df, PFAM_Index_Filter_df, on='Viral_gene_ID', how='left').fillna('NA')

    return PFAM_GENOMAD_PHROGS_df

def ADS_annotation(args, script_directory, proteins_file, hmmscan_ADS_output_file, diamond_ADS_output_file, parsed_hmmscan_ADS_output_file, parsed_diamond_ADS_output_file, unfiltered_parsed_ADS_output_file):
    hmm_ADS_db = os.path.abspath(os.path.join(args["input"], '00_DATABASES', 'dbAPIS', 'dbAPIS.hmm'))
    diamond_ADS_db = os.path.join(args["input"], '00_DATABASES', 'dbAPIS', 'APIS_db')
    parse_annotation_result_script_path = os.path.join(script_directory, 'parse_annotation_result.sh')
    ADS_db_index_path = os.path.join(args["input"], '00_DATABASES', 'dbAPIS', 'seed_family_mapping.tsv')

    if os.path.exists(unfiltered_parsed_ADS_output_file) and not args['force_ADS']:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping Anti-Defense System annotation, {unfiltered_parsed_ADS_output_file} file already exists and --force_ADS not provided...\033[0m")
        unfiltered_parsed_ADS_output_df = pd.read_csv(unfiltered_parsed_ADS_output_file, sep='\t', encoding_errors='ignore')
        unfiltered_parsed_ADS_output_df['ADS_score'] = pd.to_numeric(unfiltered_parsed_ADS_output_df['ADS_score'], errors='coerce')
        unfiltered_parsed_ADS_output_df['ADS_evalue'] = pd.to_numeric(unfiltered_parsed_ADS_output_df['ADS_evalue'], errors='coerce')
        filtered_parsed_ADS_output_df = unfiltered_parsed_ADS_output_df.loc[(unfiltered_parsed_ADS_output_df['ADS_score'] >= args['ADS_score']) & (unfiltered_parsed_ADS_output_df['ADS_evalue'] <= args['ADS_evalue'])]
        filtered_parsed_ADS_output_df = filtered_parsed_ADS_output_df.sort_values('ADS_score', ascending=False).drop_duplicates('Viral_gene_ID').sort_index()
    else:
        print(f"\n\033[1m{step_counter.print_sub_step()}: Annotating proteins against Anti-Defense System dbAPIS database using HMMER...\033[0m")
        subprocess.run(['hmmscan', '--domtblout', hmmscan_ADS_output_file, '--noali', hmm_ADS_db, proteins_file], stdout=subprocess.DEVNULL)

        print(f"\n\033[1m{step_counter.print_sub_step()}: Annotating proteins against Anti-Defense System dbAPIS database using DIAMOND...\033[0m")
        subprocess.run(['diamond', 'blastp', '--db', diamond_ADS_db, '-q', proteins_file, '-f', '6', 'qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen', 'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore', 'qlen', 'slen', '-o', diamond_ADS_output_file, '--max-target-seqs', '10000', '--threads', str(args['threads'])], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"\n\033[1m{step_counter.print_sub_step()}: Parsing HMMER and DIAMOND annotation tables...\033[0m")
        subprocess.run(['bash', parse_annotation_result_script_path, hmmscan_ADS_output_file, diamond_ADS_output_file, ADS_db_index_path, parsed_hmmscan_ADS_output_file, parsed_diamond_ADS_output_file])

        usecols = ['Viral_gene_ID', 'ADS_Hit_family', 'ADS_Defense_type', 'ADS_Hit_CLAN', 'ADS_Hit_CLAN_Defense_type', 'ADS_evalue', 'ADS_score']

        hmmscan_ADS_output_df = pd.read_csv(parsed_hmmscan_ADS_output_file, sep='\t', encoding_errors='ignore', 
                                            names=['Viral_gene_ID', 'ADS_Query_len', 'ADS_Hit_family', 'ADS_Defense_type', 'ADS_Hit_CLAN', 'ADS_Hit_CLAN_Defense_type', 'ADS_Family_len',
                                                    'ADS_evalue', 'ADS_score', 'ADS_Query_from', 'ADS_Query_to', 'ADS_HMM_from', 'ADS_HMM_to'])
        hmmscan_ADS_output_df = hmmscan_ADS_output_df[usecols]
        
        diamond_ADS_output_df = pd.read_csv(parsed_diamond_ADS_output_file, sep='\t', encoding_errors='ignore', 
                                    names=['Viral_gene_ID', 'ADS_Hit_family', 'ADS_Defense_type', 'ADS_Hit_CLAN', 'ADS_Hit_CLAN_Defense_type', 'ADS_seqid', 'ADS_pident', 'ADS_align_length',
                                        'ADS_evalue', 'ADS_score', 'ADS_qcov', 'ADS_scov'])
        diamond_ADS_output_df = diamond_ADS_output_df[usecols]
        
        unfiltered_parsed_ADS_output_df = pd.concat([hmmscan_ADS_output_df, diamond_ADS_output_df])
        unfiltered_parsed_ADS_output_df.to_csv(unfiltered_parsed_ADS_output_file, sep='\t', index=False)

        # Convert the 'score' column to numeric
        unfiltered_parsed_ADS_output_df['ADS_score'] = pd.to_numeric(unfiltered_parsed_ADS_output_df['ADS_score'], errors='coerce')
        unfiltered_parsed_ADS_output_df['ADS_evalue'] = pd.to_numeric(unfiltered_parsed_ADS_output_df['ADS_evalue'], errors='coerce')

        filtered_parsed_ADS_output_df = unfiltered_parsed_ADS_output_df.loc[(unfiltered_parsed_ADS_output_df['ADS_score'] >= args['ADS_score']) & (unfiltered_parsed_ADS_output_df['ADS_evalue'] <= args['ADS_evalue'])]
        filtered_parsed_ADS_output_df = filtered_parsed_ADS_output_df.sort_values('ADS_score', ascending=False).drop_duplicates('Viral_gene_ID').sort_index()

    return filtered_parsed_ADS_output_df

def RDRP_annotation(args, proteins_file):
    rdrp_phylogeny_dir = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', '06_RDRP_ANNOTATION')
    os.makedirs(rdrp_phylogeny_dir, exist_ok=True)
    # Load the RdRP profile HMM file
    RdRP_profile = os.path.abspath(os.path.join(args["input"], '00_DATABASES', 'RdRP_DB', 'All_RdRP_profiles_Wolf_set.22.hmm'))
    RdRP_Profile_Output = os.path.join(rdrp_phylogeny_dir, '06A_RdRP_Profile_Tab.txt')
    Formatted_RdRP_Profile_Output = os.path.join(rdrp_phylogeny_dir, '06B_Formatted_RdRP_Profile_Tab.tsv')
    Filtered_Formatted_RdRP_Profile_Output = os.path.join(rdrp_phylogeny_dir, '06C_Filtered_Formatted_RdRP_Profile_Tab.tsv')

    if os.path.exists(Filtered_Formatted_RdRP_Profile_Output) and not args["force_RdRP"]:
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping annotating proteins against RdRP HMM profiles, {Filtered_Formatted_RdRP_Profile_Output} file already exists and --force_RdRP not provided...\033[0m")
        Filtered_Formatted_RdRP_Profile_Output_df = pd.read_csv(Filtered_Formatted_RdRP_Profile_Output, sep='\t', encoding_errors='ignore')
    else:
        print(f"\n\033[1m{step_counter.print_sub_step()}: Annotating proteins against RdRP HMM profiles...\033[0m")
        subprocess.run(['hmmsearch', '-o', os.path.join(rdrp_phylogeny_dir, '06A_RdRP_Profile_Output.txt'), '--tblout', RdRP_Profile_Output, RdRP_profile, proteins_file])

        with open(os.path.join(rdrp_phylogeny_dir, '06A_RdRP_Profile_Tab.txt'), 'r') as infile:
            lines = infile.readlines()

        # Remove the first three rows and the last rows containing '#'
        lines = [line for line in lines[3:] if not line.startswith('#')]
        data = [line.strip().split() for line in lines]

        # Filter the data to keep only the desired columns if they exist
        filtered_data = []
        for row in data:
            if len(row) >= 7:
                filtered_data.append([row[0], row[2], row[4], row[5]])

        print(f"\n\033[1m{step_counter.print_sub_step()}: Creating and filtering the RdRP output tables...\033[0m")
        Formatted_RdRP_Profile_Output_df = pd.DataFrame(filtered_data, columns=["Viral_gene_ID", "RDRP_Annotation", "RDRP_evalue", "RDRP_Score"])
        Formatted_RdRP_Profile_Output_df.to_csv(Formatted_RdRP_Profile_Output, sep='\t', index=False)

        # Convert the 'score' column to numeric
        Formatted_RdRP_Profile_Output_df['RDRP_Score'] = pd.to_numeric(Formatted_RdRP_Profile_Output_df['RDRP_Score'], errors='coerce')
        Formatted_RdRP_Profile_Output_df['RDRP_evalue'] = pd.to_numeric(Formatted_RdRP_Profile_Output_df['RDRP_evalue'], errors='coerce')

        Filtered_Formatted_RdRP_Profile_Output_df = Formatted_RdRP_Profile_Output_df.sort_values('RDRP_Score').drop_duplicates('Viral_gene_ID', keep='last')
        Filtered_Formatted_RdRP_Profile_Output_df = Filtered_Formatted_RdRP_Profile_Output_df[Filtered_Formatted_RdRP_Profile_Output_df['RDRP_Score'] >= args['RdRP_score']]
        Filtered_Formatted_RdRP_Profile_Output_df = Filtered_Formatted_RdRP_Profile_Output_df[Filtered_Formatted_RdRP_Profile_Output_df['RDRP_evalue'] <= args['RdRP_evalue']]
        Filtered_Formatted_RdRP_Profile_Output_df.to_csv(Filtered_Formatted_RdRP_Profile_Output, sep='\t', index=False)

    return Filtered_Formatted_RdRP_Profile_Output_df

def merge_final_annotation_tables(args, final_annotation_output_file, PFAM_GENOMAD_PHROGS_df, Filtered_Formatted_RdRP_Profile_Output_df, filtered_parsed_ADS_output_df):
    if args['RdRP'] and args['ADS']:
        print(f"\n\033[1m{step_counter.print_main_step()}: Merging geNomad, PHROGS, PFAM, ADS, and RdRP annotation tables (filtration mode = relaxed)...\033[0m")
        RDRP_GENOMAD_PHROGS_PFAM_df = pd.merge(PFAM_GENOMAD_PHROGS_df, Filtered_Formatted_RdRP_Profile_Output_df[["Viral_gene_ID", "RDRP_Annotation", "RDRP_evalue", "RDRP_Score"]], on='Viral_gene_ID', how='left').fillna('NA')
        RDRP_GENOMAD_PHROGS_PFAM_df.insert(12, 'RDRP_Annotation', RDRP_GENOMAD_PHROGS_PFAM_df.pop('RDRP_Annotation'))
        RDRP_GENOMAD_PHROGS_PFAM_ADS_df = pd.merge(RDRP_GENOMAD_PHROGS_PFAM_df, filtered_parsed_ADS_output_df, on='Viral_gene_ID', how='left').fillna('NA')
        RDRP_GENOMAD_PHROGS_PFAM_ADS_df.insert(13, 'ADS_Hit_family', RDRP_GENOMAD_PHROGS_PFAM_ADS_df.pop('ADS_Hit_family'))
        RDRP_GENOMAD_PHROGS_PFAM_ADS_df.insert(14, 'ADS_Defense_type', RDRP_GENOMAD_PHROGS_PFAM_ADS_df.pop('ADS_Defense_type'))
        desired_column_order = ['Viral_gene_ID', 'Contig_name', 'Gene_number', 'start', 'end', 'length', 'strand', 'GENOMAD_Annotation', 'PHROGS_Annotation', 'PHROGS_Category', 'PFAM_Annotation',	'PFAM_Category', "RDRP_Annotation",
                                'ADS_Hit_family', 'ADS_Defense_type', 'GENOMAD_Annotation_accessions', 'GENOMAD_Score', 'GENOMAD_evalue', 'GENOMAD_gc_content', 'GENOMAD_genetic_code', 'GENOMAD_rbs_motif', 'GENOMAD_marker',
                                'GENOMAD_virus_hallmark', 'GENOMAD_Annotation_amr', 'PHROGS_Score', 'PHROGS_evalue', 'PHROGS_seqIdentity', 'PHROGS_RefSeq_Annotation', 'PHROGS_Pfam_Annotation',
                                'PHROGS_GO_Annotation', 'PHROGS_KO_Annotation', 'PFAM_Accession_Number', 'PFAM_Annotation_Short', 'PFAM_seqIdentity', 'PFAM_Score', 'PFAM_evalue', "RDRP_evalue", "RDRP_Score", 'ADS_Hit_CLAN', 'ADS_Hit_CLAN_Defense_type', 'ADS_evalue', 'ADS_score']
        RDRP_GENOMAD_PHROGS_PFAM_ADS_df = RDRP_GENOMAD_PHROGS_PFAM_ADS_df[desired_column_order]
        RDRP_GENOMAD_PHROGS_PFAM_ADS_df.to_csv(final_annotation_output_file, sep='\t', index=False)
    elif args['RdRP']:
        print(f"\n\033[1m{step_counter.print_main_step()}: Merging geNomad, PHROGS, PFAM, and RdRP annotation tables (filtration mode = relaxed)...\033[0m")
        RDRP_GENOMAD_PHROGS_PFAM_df = pd.merge(PFAM_GENOMAD_PHROGS_df, Filtered_Formatted_RdRP_Profile_Output_df[["Viral_gene_ID", "RDRP_Annotation", "RDRP_evalue", "RDRP_Score"]], on='Viral_gene_ID', how='left').fillna('NA')
        RDRP_GENOMAD_PHROGS_PFAM_df.insert(12, 'RDRP_Annotation', RDRP_GENOMAD_PHROGS_PFAM_df.pop('RDRP_Annotation'))
        RDRP_GENOMAD_PHROGS_PFAM_df.to_csv(final_annotation_output_file, sep='\t', index=False)
    elif args['ADS']:
        print(f"\n\033[1m{step_counter.print_main_step()}: Merging geNomad, PHROGS, PFAM, and ADS annotation tables (filtration mode = relaxed)...\033[0m")
        ADS_GENOMAD_PHROGS_PFAM_df = pd.merge(PFAM_GENOMAD_PHROGS_df, filtered_parsed_ADS_output_df, on='Viral_gene_ID', how='left').fillna('NA')
        desired_column_order = ['Viral_gene_ID', 'Contig_name', 'Gene_number', 'start', 'end', 'length', 'strand', 'GENOMAD_Annotation', 'PHROGS_Annotation', 'PHROGS_Category', 'PFAM_Annotation',	'PFAM_Category',
                                'ADS_Hit_family', 'ADS_Defense_type', 'GENOMAD_Annotation_accessions', 'GENOMAD_Score', 'GENOMAD_evalue', 'GENOMAD_gc_content', 'GENOMAD_genetic_code', 'GENOMAD_rbs_motif', 'GENOMAD_marker',
                                'GENOMAD_virus_hallmark', 'GENOMAD_Annotation_amr', 'PHROGS_Score', 'PHROGS_evalue', 'PHROGS_seqIdentity', 'PHROGS_RefSeq_Annotation', 'PHROGS_Pfam_Annotation',
                                'PHROGS_GO_Annotation', 'PHROGS_KO_Annotation', 'PFAM_Accession_Number', 'PFAM_Annotation_Short', 'PFAM_seqIdentity', 'PFAM_Score', 'PFAM_evalue', 'ADS_Hit_CLAN', 'ADS_Hit_CLAN_Defense_type', 'ADS_evalue', 'ADS_score']
        ADS_GENOMAD_PHROGS_PFAM_df = ADS_GENOMAD_PHROGS_PFAM_df[desired_column_order]
        ADS_GENOMAD_PHROGS_PFAM_df.to_csv(final_annotation_output_file, sep='\t', index=False)
    else:
        print(f"\n\033[1m{step_counter.print_main_step()}: Merging geNomad, PHROGS, and PFAM annotation tables (filtration mode = relaxed)...\033[0m")
        PFAM_GENOMAD_PHROGS_df.to_csv(final_annotation_output_file, sep='\t', index=False)

    print(f"Final annotation table {final_annotation_output_file} created!") 

def conservative_mode_final_table(args, final_annotation_output_file):
    # Define the filtration argument used in Module 05
    summary_report_path_module_05 = os.path.join(args['input'], '05_VOTU_TABLES', 'MVP_05_Summary_Report.txt')
    module_05_summary_content = ""
    if os.path.exists(summary_report_path_module_05):  # We need this test in case users ran module 01 - 02 - 03 then 06 (without 04 / 05)
    
        with open(summary_report_path_module_05, 'r') as module_05_summary_report:
            module_05_summary_content = module_05_summary_report.read()

        target_line = next((line for line in module_05_summary_content.split('\n') if line.startswith('05_create_votu_table.py')), None)
        filtration_option = re.search(r'--filtration (\w+)', target_line).group(1) if target_line else None

        if filtration_option == 'conservative':
            final_relaxed_functional_annotation_df = pd.read_csv(final_annotation_output_file, sep='\t', encoding_errors='ignore')
            filtered_conservative_vOTUs_path = os.path.join(args['input'], '05_VOTU_TABLES', 'MVP_05_All_Sample_Filtered_conservative_Representative_Virus_Proviruses_vOTU_RPKM_Table.tsv')
            filtered_conservative_vOTUs_df = pd.read_csv(filtered_conservative_vOTUs_path, sep='\t', encoding_errors='ignore')
            final_conservative_functional_annotation_df = pd.merge(filtered_conservative_vOTUs_df[["virus_id"]], final_relaxed_functional_annotation_df, how="left", left_on="virus_id", right_on="Contig_name")
            final_conservative_functional_annotation_df = final_conservative_functional_annotation_df.drop(columns=['virus_id'])
            final_conservative_functional_annotation_path = final_annotation_output_file.replace("Relaxed", "Conservative")
            final_conservative_functional_annotation_df.to_csv(final_conservative_functional_annotation_path, sep='\t', index=False)
    else:
        filtration_option = "none"
    
    # Calculate summary statistics
    if filtration_option == 'conservative':
        print(f"\n\033[1m{step_counter.print_main_step()}: Filtering final annotation tables based on conservative mode if used in Module 05...\033[0m")
        final_annotation_output_file_df = pd.read_csv(final_conservative_functional_annotation_path, sep='\t', encoding_errors='ignore')
    else:
        print(f"\n\033[1m{step_counter.print_main_step()}: Filtering final annotation tables based on relaxed mode (used in Module 05)...\033[0m")
        final_annotation_output_file_df = pd.read_csv(final_annotation_output_file, sep='\t', encoding_errors='ignore')

    return final_annotation_output_file_df

def guess_vs_hallmark(vec):
    if vec['GENOMAD_marker'] == "NA" or pd.isna(vec['GENOMAD_marker']):
        return "-"
    t = vec['GENOMAD_marker'].split(".")
    if t[2].startswith("V") or t[2].endswith("V"):
        # We have a virus gene, is it hallmark ? (note - hallmark coded as 0 in VirSorter, 1 in geNomad)
        if vec['GENOMAD_virus_hallmark'] == 1:
            return "0"
        else:
            return "1"
    else:
        return "-"

def get_contig_name(gene_name):
            x = gene_name.split("_")
            return "_".join(x[:-1])

def add_line(vec, outwriter):
    # Convert strand notation in VirSorter format (plus and minus)
    if vec['strand'] == -1:
        strand = "-"
    elif vec["strand"] == 1:
        strand = "+"
    # Convert marker gene name if na
    if vec['VS_hallmark'] == "-":
        vec['GENOMAD_marker'] = "-"
        vec['GENOMAD_Score'] = "-"
        vec['GENOMAD_evalue'] = "-"

    if pd.isna(vec['PFAM_Annotation_Short']):
        PFAM_Annotation_Short = "-"
        PFAM_Score = "-"
        PFAM_evalue = "-"
    else:
        PFAM_Annotation_Short = vec['PFAM_Annotation_Short']
        PFAM_Score = vec['PFAM_Score']
        PFAM_evalue = vec['PFAM_evalue']

    outwriter.writerow(
        [vec['Viral_gene_ID'], vec['start'], vec['end'], vec['length'], strand, vec['GENOMAD_marker'],
            vec['GENOMAD_Score'], vec['GENOMAD_evalue'], vec['VS_hallmark'], PFAM_Annotation_Short, PFAM_Score,
            PFAM_evalue])
    
def write_output(df, outwriter, output_handle):
    # First add a line for the contig itself
    contig = df['contig'].unique()[0]
    n_gene = len(df)
    output_handle.write(f">{contig}|{n_gene}|l\n")  # Note - we falsely claim all sequences are linear, it does not matter really for DRAM-V downstream
    # Now adding one line for each gene, sorted by start
    df.sort_values(['start', 'strand'], ascending=[True, True]).apply(lambda x: add_line(x, outwriter), axis=1)
            
def create_DRAM_inputs(args, genomad_annotation, sequence_file, final_annotation_output_file):
    # Create a file to be processed through DRAM-v if --DRAM flag is provided
    dram_v_folder = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', '06_DRAM_V')
    DRAM_input_file = os.path.join(dram_v_folder, os.path.splitext(os.path.basename(genomad_annotation))[0] + '_DRAM_Input.tsv')
    sequence_output_file = os.path.join(dram_v_folder, os.path.splitext(os.path.basename(sequence_file))[0] + '_DRAM_Input.fna')

    if args['DRAM']:
        print(f"\n\033[1m{step_counter.print_main_step()}: Generating input files for DRAM-v functional annotation analysis...\033[0m")
        os.makedirs(dram_v_folder, exist_ok=True)  # Create the folder if it doesn't exist

        records = list(SeqIO.parse(sequence_file, "fasta"))

        with open(sequence_output_file, "w") as output_handle:
            for record in records:
                # Replace '|' characters with '_' in the sequence header
                modified_header = record.id.replace('|', '_') + '-cat_1'

                # Write a single line with both the original and modified headers
                output_handle.write(f">{modified_header} {record.id}\n{record.seq}\n")

        annotation_df = pd.read_csv(final_annotation_output_file, sep='\t', encoding_errors='ignore',
                                    usecols=['Viral_gene_ID', 'start', 'end', 'length', 'strand',
                                                'GENOMAD_marker',
                                                'GENOMAD_Score', 'GENOMAD_evalue', 'GENOMAD_virus_hallmark',
                                                'PFAM_Annotation', 'PFAM_Annotation_Short', 'PFAM_Accession_Number',
                                                'PFAM_Score', 'PFAM_evalue'])
        # Replace '|' characters with '_' in 'Viral_gene_ID' column
        annotation_df['Viral_gene_ID'] = annotation_df['Viral_gene_ID'].str.replace('|', '_')
        # Add info about hallmark gene in the VirSorter format
        annotation_df['VS_hallmark'] = annotation_df[['GENOMAD_marker', 'GENOMAD_virus_hallmark']].apply(lambda x: guess_vs_hallmark(x), axis=1)
        # Also add info about the original contig
        annotation_df['contig'] = annotation_df['Viral_gene_ID'].apply(lambda x: get_contig_name(x))
        # Prepare the output file
        with open(DRAM_input_file, "w") as output_handle:
            outwriter = csv.writer(output_handle, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
            annotation_df.groupby('contig').apply(lambda x: write_output(x, outwriter, output_handle))

def delete_files(args, temp_directory):
    print(f"\n\033[1m{step_counter.print_main_step()}: Deleting temporary files...\033[0m")
    # Define the directory where you want to remove files
    directory_to_clean = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION')
    # Remove temporary files and folders
    for filename in os.listdir(directory_to_clean):
        if filename.endswith(('.faa', '.tsv', '.txt')):
            continue  # Keep .faa, .tsv, and .txt files
        file_path = os.path.join(directory_to_clean, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Remove temporary files and folders
    if os.path.exists(temp_directory):
        shutil.rmtree(temp_directory)

def generate_summary_report(args, final_annotation_output_file_df, phrogs_output_file, mvp_start_time, mvp_end_time):
    print(f"\n\033[1m{step_counter.print_main_step()}: Creating the summary report for Module 06...\033[0m")
    # Calculate the number of genes and hits
    num_genes = len(final_annotation_output_file_df)
    num_hit_genes = len(phrogs_output_file)

    # Count occurrences of each category in the PHROGS_Category column
    category_levels = final_annotation_output_file_df['PHROGS_Category']
    category_counts = category_levels.value_counts()
    # Calculate the percentage of each category
    taxa_percentages = (category_counts / num_genes) * 100
    # Prepare the summary report content
    category_summary = "\n".join([f"{category}: {count} ({percentage:.1f}%)" for category, count, percentage in zip(category_counts.index, category_counts.values, taxa_percentages.values)])

    # Module 06 header
    module_06_header = """****************************************************************************
******************               MODULE 06                ******************
****************************************************************************
"""

    # Create a dictionary to hold argument descriptions and their default values
    argument_defaults = {
        '--input': args['input'],
        '--metadata': args['metadata'],
        '--fasta_files': args['fasta_files'],
        '--delete_files': args['delete_files'],
        '--PHROGS_evalue': args['PHROGS_evalue'],
        '--PHROGS_score': args['PHROGS_score'],
        '--PFAM_evalue': args['PFAM_evalue'],
        '--PFAM_score': args['PFAM_score'],
        '--ADS': args['ADS'],
        '--ADS_evalue': args['ADS_evalue'],
        '--ADS_score': args['ADS_score'],
        '--RdRP': args['RdRP'],
        '--RdRP_evalue': args['RdRP_evalue'],
        '--RdRP_score': args['RdRP_score'],
        '--DRAM': args['DRAM'],
        '--force_prodigal': args['force_prodigal'],
        '--force_PHROGS': args['force_PHROGS'],
        '--force_PFAM': args['force_PFAM'],
        '--force_ADS': args['force_ADS'],
        '--force_RdRP': args['force_RdRP'],
        '--force_outputs': args['force_outputs'],
        '--threads': args['threads']
    }

    # Write a summary line with script arguments and their default values
    summary_line = "06_do_functional_annotation.py"
    for arg, default in argument_defaults.items():
        if default is not None:
            summary_line += f" {arg} {default}"

    # Calculate duration
    duration = mvp_end_time - mvp_start_time
    formatted_start_time = mvp_start_time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_end_time = mvp_end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Prepare the complete summary content
    complete_summary_content = f"""
\nSummary Report of the functional annotation after filtration
--------------------------
Number of genes: {num_genes}
Number of hits against PHROGS db: {num_hit_genes}

Gene category summary:
{category_summary}
"""

    summary_report_path_module_06 = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', 'MVP_06_Summary_Report.txt')

    # Write the combined content to the new summary report for Module 06
    with open(summary_report_path_module_06, 'w') as module_06_summary_report:
        module_06_summary_report.write(module_06_header)
        module_06_summary_report.write(summary_line)
        module_06_summary_report.write(f"\n")
        module_06_summary_report.write(f"\nStart Time: {formatted_start_time}\n")
        module_06_summary_report.write(f"End time: {formatted_end_time}\n")
        module_06_summary_report.write(f"Running Time: {duration.total_seconds():.2f} seconds\n")
        module_06_summary_report.write(complete_summary_content)

def main(args): 
    # Capture start time
    mvp_start_time = datetime.datetime.now()
    mvp_formatted_start_time = mvp_start_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nStart Time: {mvp_formatted_start_time}") 

    script_directory, proteins_file, sequence_file, final_annotation_output_file, phrogs_output_file, temp_directory, pfam_output_file, genomad_annotation, hmmscan_ADS_output_file, diamond_ADS_output_file, parsed_hmmscan_ADS_output_file, parsed_diamond_ADS_output_file, unfiltered_parsed_ADS_output_file = set_up_paths(args)

    if not args['force_outputs'] and os.path.exists(final_annotation_output_file):
        print(f"\n\033[1m{step_counter.print_main_step()}: Skipping functional annotation steps beacause {final_annotation_output_file}' exists, and --force_outputs argument not provided...\033[0m")
    else:
        predict_protein(args, proteins_file, sequence_file)

        target_sequences = generate_target_sequence(proteins_file)

        phrogs_annotation(args, proteins_file, target_sequences,  phrogs_output_file, temp_directory)

        pfam_annotation(args, proteins_file, target_sequences, pfam_output_file, temp_directory)

        PFAM_GENOMAD_PHROGS_df = merge_phrogs_pfam_tables(args, phrogs_output_file, genomad_annotation, pfam_output_file)

        # ADS prediction
        if args['ADS']:
            filtered_parsed_ADS_output_df = ADS_annotation(args, script_directory, proteins_file, hmmscan_ADS_output_file, diamond_ADS_output_file, parsed_hmmscan_ADS_output_file, parsed_diamond_ADS_output_file, unfiltered_parsed_ADS_output_file)
        else:
            filtered_parsed_ADS_output_df = None

        # Create the "07_RDRP_PHYLOGENY" directory if --RdRP flag is provided
        if args['RdRP']:
            Filtered_Formatted_RdRP_Profile_Output_df = RDRP_annotation(args, proteins_file)
        else:
            Filtered_Formatted_RdRP_Profile_Output_df = None

        merge_final_annotation_tables(args, final_annotation_output_file, PFAM_GENOMAD_PHROGS_df, Filtered_Formatted_RdRP_Profile_Output_df, filtered_parsed_ADS_output_df)

    final_annotation_output_file_df = conservative_mode_final_table(args, final_annotation_output_file)

    create_DRAM_inputs(args, genomad_annotation, sequence_file, final_annotation_output_file)

    if args['delete_files']:
        delete_files(args, temp_directory)

    # Capture end time
    mvp_end_time = datetime.datetime.now()
    mvp_formatted_end_time = mvp_end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate duration
    mvp_duration = mvp_end_time - mvp_start_time

    generate_summary_report(args, final_annotation_output_file_df, phrogs_output_file, mvp_start_time, mvp_end_time)

    message1 = f"\033[1mModule 06 finished: functional annotation done and summary report generated!\033[0m"
    message2 = f"Final annotation table {final_annotation_output_file} has been created."
    message3 = f"MVP_06_summary_report.txt saved in {args['input']}/06_FUNCTIONAL_ANNOTATION."
    line_of_stars = '*' * len(message1)
    print()
    print(line_of_stars)
    print(message1)
    print(f"\nStart Time: {mvp_formatted_start_time}") 
    print(f"End Time: {mvp_formatted_end_time}")
    print(f"Running Time: {mvp_duration.total_seconds():.2f} seconds\n")
    print(message2)
    print(message3)
    print(line_of_stars)
    print()

    print("Please don't forget to cite MVP and the following software used by this module:")
    print("- Hyatt, D. et al. Prodigal: Prokaryotic Gene Recognition and Translation Initiation Site Identification. BMC Bioinformatics. 2010, 11(1). https://doi.org/10.1186/1471-2105-11-119.\n")
    print("- Mirdita, M. et al. Fast and sensitive taxonomic assignment to metagenomic contigs. Bioinformatics. 2021, 37(18). https://doi.org/10.1093/bioinformatics/btab184\n")
    print("- Potter, S. et al. HMMER Web Server: 2018 Update. Nucleic Acids Research. 2018, 46(1). https://doi.org/10.1093/nar/gky448.\n")
