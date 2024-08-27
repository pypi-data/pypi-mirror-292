#!/usr/bin/env python3

import argparse
import os
import glob
import pandas as pd
from functools import reduce
import numpy as np
import datetime
import time
import mvip

def fetch_arguments(parser):
    parser.set_defaults(func=main)
    parser.set_defaults(program="MVP_05_create_vOTU_table")
    parser.add_argument(
        "--input", "-i",
        help="Path to your working directory where you want to run MVP.",
    )
    parser.add_argument(
        "--metadata", "-m",
        help="Path to your metadata that you want to use to run MVP.",
    )
    parser.add_argument(
        '--covered_fraction',
        nargs='+',
        type=float,
        default=[0.1, 0.5, 0.9],
        help='minimum covered fraction for filtering Default: 0.1 0.5 0.9')
    parser.add_argument(
        "--normalization",
        type=str,
        default='RPKM',
        choices=['RPKM', 'FPKM'],
        help="Metrics to normalize",
    )
    parser.add_argument(
        "--filtration",
        type=str,
        default='conservative',
        choices=['relaxed', 'conservative'],
        help="Filtration level (relaxed or conservative). Default = conservative",
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

def merge_coverm_tables(args):
    print(f"\n\033[1m{step_counter.print_main_step()}: Merging all CoverM tables generated in Module 04 (read mapping)...\033[0m")
    # Combine all CoverM CSV files into one
    read_mapping_dir = os.path.join(args['input'], '04_READ_MAPPING', '*', '*_CoverM.tsv')
    all_coverm_csv = glob.glob(read_mapping_dir, recursive=True)
    dfs = []

    for filename in all_coverm_csv:
        df = pd.read_csv(filename, sep='\t', usecols=['Sample', 'Contig', 'Covered Fraction', 'Length', args['normalization']])
        df = df.drop_duplicates(subset=['Sample', 'Contig', 'Length'], keep='last')
        df = df.pivot(index=['Contig', 'Length'], columns='Sample')
        df.columns = ['_'.join(str(col) for col in cols).strip() for cols in df.columns.values]
        dfs.append(df)

    df_coverm_merged = reduce(lambda left, right: pd.merge(left, right, on=['Contig', 'Length'], how='outer'), dfs).reset_index()

    # Read the quality summary TXT file
    quality_summary_concatenated_df_path = os.path.join(args['input'], '03_CLUSTERING', 'MVP_03_All_Sample_Unfiltered_Merged_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv')
    merged_quality_summary_concatenated_df = pd.read_csv(quality_summary_concatenated_df_path, sep='\t')

    # Merge the CoverM and TSV dataframes
    df_merged = pd.merge(merged_quality_summary_concatenated_df, df_coverm_merged, left_on='virus_id', right_on='Contig', how='right')
    df_merged = df_merged.loc[:, ~df_merged.columns.duplicated(keep='last')]
    df_merged['completeness'].fillna(0, inplace=True)  # When no completeness, set it at 0 so that the sequence does not get filtered out

    # Remove columns that are in the columns_to_exclude list
    columns_to_exclude = ['Contig', 'Length']
    df_merged = df_merged.drop(columns=columns_to_exclude)

    # Save the merged DataFrame as a CSV file in the output folder
    output_filtered_file_path = os.path.join(args['input'], '05_VOTU_TABLES', f'MVP_05_All_Sample_Filtered_{args["filtration"]}_Representative_Virus_Proviruses_vOTU_{args["normalization"]}_Table.tsv')
    os.makedirs(os.path.dirname(output_filtered_file_path), exist_ok=True)
    df_merged.to_csv(output_filtered_file_path, sep='\t', index=False)

    return df_merged, output_filtered_file_path

def filter_coverm_table(df_merged, output_filtered_file_path, args):
    if args['filtration'] == 'conservative':
        print(f"\n\033[1m{step_counter.print_main_step()}: Filtering the merged CoverM table using the conservative mode...\033[0m")
    else:
        print(f"\n\033[1m{step_counter.print_main_step()}: Filtering the merged CoverM table using the relaxed mode...\033[0m")
    # Apply relaxed filtration criteria
    df_filtered = df_merged.loc[(df_merged['viral_genes'] >= args['viral_min_genes'])]
    df_filtered = df_filtered.loc[df_filtered['host_genes']/df_filtered['viral_genes'] <= args['host_viral_genes_ratio']]

    # Apply the new filtration logic if args.filtration is conservative
    if args['filtration'] == 'conservative':
        df_filtered = df_filtered.loc[
            (((df_filtered['completeness_method'].str.contains('AAI-based')) | (df_filtered['completeness_method'].str.contains('DTR'))) &
             (df_filtered['checkv_quality'].isin(['High-quality', 'Medium-quality']))) | (df_filtered['virus_length'] > 5000)]
    
    # Save the filtered DataFrame as a CSV file in the output folder
    df_filtered.to_csv(output_filtered_file_path, sep='\t', index=False)

    return df_filtered

# Define a function to filter and update RPKM columns based on covered fraction
def filter_and_update_RPKM(row, cf, covered_fraction_cols, TPM_cols):
    for sample, cf_col in enumerate(covered_fraction_cols):
        cf_val = row[cf_col]
        print(f"Value: {cf}, Type: {type(cf)}")
        print(f"Value: {cf_val}, Type: {type(cf_val)}")
        if cf_val < cf:
            tpm_col = TPM_cols[sample]
            row[tpm_col] = 0
    return row

def filter_by_coverage_tables(df_filtered, args):
    print(f"\n\033[1m{step_counter.print_main_step()}: Filtering the merged CoverM table using the horizontal coverage and generating a set of final coverage tables...\033[0m")

    df_filtered_list = []
    
    print(f"Value: {args['covered_fraction']}, Type: {type(args['covered_fraction'])}")

    for cf in args['covered_fraction']:
        # Make a copy of df_filtered so that we don't modify it directly
        df_temp = df_filtered.copy()
        covered_fraction_cols = df_temp.filter(like='Covered Fraction').columns
        TPM_cols = df_temp.filter(like=args['normalization']).columns

        # Apply the filter_and_update_RPKM function to each row
        df_temp = df_temp.apply(filter_and_update_RPKM, args=(cf, covered_fraction_cols, TPM_cols), axis=1)
        
        # Filter out rows where all TPM values are 0
        df_temp = df_temp[~(df_temp[TPM_cols] == 0).all(axis=1)]
        df_temp = df_temp.loc[:, ~df_temp.columns.str.contains('Covered Fraction')]
        df_filtered_list.append(df_temp)

    # Save the filtered dataframes
    for i, cf in enumerate(args['covered_fraction']):
        output_file = os.path.join(args['input'], '05_VOTU_TABLES', f'MVP_05_All_Sample_Filtered_{args["filtration"]}_HC_{cf}_Representative_Virus_Proviruses_vOTU_{args["normalization"]}_Table.tsv')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df_filtered_list[i].to_csv(output_file, sep='\t', index=False)

def generate_summary_report(df_filtered, args, formatted_start_time, formatted_end_time, duration):
    print(f"\n\033[1m{step_counter.print_main_step()}: Creating the summary report for Module 05...\033[0m")
    # Calculate summary statistics
    num_vOTUs = len(df_filtered)
    num_proviruses = (df_filtered['provirus'].str.contains('Yes', case=False)).sum()
    mean_length = df_filtered['virus_length'].mean()
    max_length = df_filtered['virus_length'].max()
    min_length = df_filtered['virus_length'].min()
    quality_counts = df_filtered['checkv_quality'].value_counts()

    # Add columns and counts for RPKM statistics
    rpkm_columns = [col for col in df_filtered.columns if col.startswith('RPKM_')]
    rpkm_virus_counts = [(col, (df_filtered[col] > 0).sum()) for col in rpkm_columns]
    # Sort RPKM counts in descending order
    rpkm_virus_counts.sort(key=lambda x: x[1], reverse=True)

    # Count occurrences of each realm in the second level of the taxonomy column
    taxa_levels = df_filtered['taxonomy'].str.split(';')
    second_level_taxa = taxa_levels.apply(lambda x: x[1] if len(x) > 1 else 'Unclassified/others')
    taxa_counts = second_level_taxa.value_counts()
    # Calculate the percentage of each realm
    taxa_percentages = (taxa_counts / num_vOTUs) * 100
    # Prepare the summary report content
    taxa_summary = "\n".join([f"{realm}: {count} ({percentage:.1f}%)" for realm, count, percentage in zip(taxa_counts.index, taxa_counts.values, taxa_percentages.values)])

    # Prepare the summary report content for top classes
    taxa_levels = df_filtered['taxonomy'].str.split(';').apply(lambda levels: levels + [''] * (5 - len(levels)))
    fifth_level_classes = taxa_levels.apply(lambda x: x[4])
    filtered_classes = fifth_level_classes[(fifth_level_classes != '') & (fifth_level_classes != 'Unclassified')]
    class_counts = filtered_classes.value_counts()
    top_10_classes = class_counts.nlargest(10)
    top_classes_summary = "\n".join([f"{cls}: {count}" for cls, count in top_10_classes.items()])

    # Define the additional lines you want to add to the summary report
    module_05_header = """****************************************************************************
******************               MODULE 05                ******************
****************************************************************************
"""

    # Create a dictionary to hold argument descriptions and their default values
    argument_defaults = {
        '--input': args['input'],
        '--metadata': args['metadata'],
        '--covered_fraction': args['covered_fraction'],
        '--normalization': args['normalization'],
        '--filtration': args['filtration'],
        '--viral-min-genes': args['viral_min_genes'],
        '--host-viral-genes-ratio': args['host_viral_genes_ratio']
    }

    # Write a summary line with script arguments and their default values
    summary_line = "05_create_votu_table.py"
    for arg, default in argument_defaults.items():
        if default is not None:
            summary_line += f" {arg} {default}"

    complete_summary_content = f"""
    \nSummary Report after both clustering and filtration
    --------------------------
    Number of vOTUs: {num_vOTUs}, including {num_proviruses} proviruses
    Mean vOTUs Length: {mean_length:.2f}
    Max vOTUs Length: {max_length}
    Min vOTUs Length: {min_length}

    vOTUs CheckV quality summary:
    Low Quality: {quality_counts.get('Low-quality', 0)}
    Medium Quality: {quality_counts.get('Medium-quality', 0)}
    High Quality: {quality_counts.get('High-quality', 0)}
    Complete: {quality_counts.get('Complete', 0)}
    Not determined: {quality_counts.get('Not-determined', 0)}

    vOTUs taxonomy summary:
    {taxa_summary}

    vOTUs Top 10 classes:
    {top_classes_summary}
    """

    summary_report_path_module_05 = os.path.join(args['input'], '05_VOTU_TABLES', 'MVP_05_Summary_Report.txt')

    # Write the combined content to the new summary report for Module 02
    with open(summary_report_path_module_05, 'w') as module_05_summary_report:
        module_05_summary_report.write(module_05_header + summary_line)
        module_05_summary_report.write(f"\n")
        module_05_summary_report.write(f"\nStart Time: {formatted_start_time}\n")
        module_05_summary_report.write(f"End time: {formatted_end_time}\n")
        module_05_summary_report.write(f"Running Time: {duration.total_seconds():.2f} seconds\n")
        module_05_summary_report.write(complete_summary_content)

def main (args):
    # Capture start time
    mvp_start_time = datetime.datetime.now()
    mvp_formatted_start_time = mvp_start_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nStart Time: {mvp_formatted_start_time}") 

    df_merged, output_filtered_file_path = merge_coverm_tables(args)

    df_filtered = filter_coverm_table(df_merged, output_filtered_file_path, args)

    filter_by_coverage_tables(df_filtered, args)

    # Capture end time
    mvp_end_time = datetime.datetime.now()
    mvp_formatted_end_time = mvp_end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate duration
    mvp_duration = mvp_end_time - mvp_start_time

    generate_summary_report(df_filtered, args, mvp_formatted_start_time, mvp_formatted_end_time, mvp_duration)

    message1 = "\033[1mModule 05 finished: vOTU tables and summary report generated!\033[0m\n"
    message2 = f"Output vOTU tables and summary report file have been saved in the {args['input']}/05_VOTU_TABLES directory."
    message3 = "\n\033[1mWe hope you enjoyed using MVP script, and you can now explore your data!\033[0m"
    line_of_stars = '*' * len(message2)
    print()
    print(line_of_stars)
    print(message1)
    print(f"Start Time: {mvp_formatted_start_time}") 
    print(f"End Time: {mvp_formatted_end_time}")
    print(f"Running Time: {mvp_duration.total_seconds():.2f} seconds\n")
    print(message2)
    print(message3)
    print(line_of_stars)
    print()

    print("Please don't forget to cite the MVP script!\n")
