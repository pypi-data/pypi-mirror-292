import argparse
import os
import subprocess
import sys
from os.path import getsize
import pandas as pd
from functools import reduce
from Bio import SeqIO
from tqdm import tqdm
import pkg_resources
import datetime
import time
import mvip

def fetch_arguments(parser):
    parser.set_defaults(func=main)
    parser.set_defaults(program="MVP_00_set_up_MVP")
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Path to the working directory where MVP will be run.",
    )
    parser.add_argument(
        "--metadata", "-m",
        type=str,
        help="Path to the metadata that will be use to run MVP.",
    )
    parser.add_argument(
        "--skip_install_databases",
        action="store_true",
        default=False,
        help="Install geNomad and CheckV databases in the respective repositories. (default = False).",
    )
    parser.add_argument(
        '--genomad_db_path', 
        type=str,
        help='Path to the directory where geNomad database will be installed.'
        )
    parser.add_argument(
        '--checkv_db_path', 
        type=str,
        help='Path to the directory where CheckV database will be installed.'
        )
    parser.add_argument(
        "--skip_check_errors",
        action="store_true",
        default=False,
        help="Skip to run sequence data error checking. (default = False).",
    )
    
# Global variable to track the current step number
current_step = 0
# Dictionary to track sub-step counts for each function
sub_step_counts = {}

def print_step(func_name):
    global current_step
    # If it's the first call to this function, increment the step number
    if func_name not in sub_step_counts:
        current_step += 1
        sub_step_counts[func_name] = 1
        return f"Step {current_step}"  # Return without a letter for the first call
    else:
        # Increment the sub-step count for subsequent calls within the same function
        sub_step_counts[func_name] += 1
        sub_step_letter = chr(64 + sub_step_counts[func_name])  # 'A' is 65 in ASCII
        return f"Step {current_step}{sub_step_letter}"


def convert_metadata_to_unix(args):
    print(f"\n\033[1m{print_step(convert_metadata_to_unix)}: Converting the metadata file...\033[0m")

    subprocess.run(['dos2unix', args["metadata"]])

def check_metadata(args):
    print(f"\n\033[1m{print_step(check_metadata)}: Checking for missing, incorrectly named mandatory columns or extra columns in the metadata file...\033[0m")

    # Read the metadata file
    metadata = pd.read_csv(args["metadata"], sep='\t')

    # Define the mandatory and optional columns
    mandatory_columns = ['Sample_number', 'Sample', 'Assembly_Path', 'Read_Path']
    optional_columns = ['Variable']

    missing_columns = [col for col in mandatory_columns if col not in metadata.columns]
    if missing_columns:
        print(f"Error: Missing mandatory column(s) in metadata: {', '.join(missing_columns)}")
        sys.exit(1)

    # Check for extra columns
    extra_columns = [col for col in metadata.columns if col not in mandatory_columns + optional_columns]
    if extra_columns:
        print(f"Error: Extra column(s) found in metadata: {', '.join(extra_columns)}")
        sys.exit(1)

    print("The metadata looks fine. Proceeding to the next steps.")

def check_paths(args):
    print(f"\n\033[1m{print_step(check_paths)}: Checking if the assembly or read file paths provided in the metadata are correct...\033[0m")

    metadata = pd.read_csv(args["metadata"], sep='\t')
    nonexistent_assembly_paths = metadata.loc[~metadata['Assembly_Path'].apply(lambda path: path == '' or (isinstance(path, str) and os.path.exists(path))), 'Assembly_Path']
    nonexistent_read_paths = metadata.loc[~metadata['Read_Path'].apply(lambda path: path == '' or (isinstance(path, str) and os.path.exists(path))), 'Read_Path']

    if not nonexistent_assembly_paths.empty or not nonexistent_read_paths.empty:
        if not nonexistent_assembly_paths.empty:
            print(f"Error: The following Assembly_Path values correspond to non-existent files: {', '.join(nonexistent_assembly_paths)}")
        if not nonexistent_read_paths.empty:
            nonexistent_read_paths_str = nonexistent_read_paths.astype(str)
            print(f"Error: The following Read_Path values correspond to non-existent files: {', '.join(nonexistent_read_paths_str)}")
        sys.exit(1)
    
    print("The assembly and read file paths are correct. Proceeding to the next steps.")

def check_sequence_data(args):
    if args["skip_check_errors"]:
        print(f"\n\033[1m{print_step(check_sequence_data)}: Skipping verifying that the input assembly files contain only valid nucleotide characters and do not have duplicate headers...\033[0m")
        return
    
    print(f"\n\033[1m{print_step(check_sequence_data)}: Verifying that the input assembly files contain only valid nucleotide characters and does not have duplicate headers...\033[0m")
    metadata = pd.read_csv(args["metadata"], sep='\t')
    for row_index, (_, row) in enumerate(metadata.iterrows(), start=1):
        input_assembly_file = row['Assembly_Path']
        
        with open(input_assembly_file, "r") as input_fasta:
            headers_seen = set()
            invalid_chars_found = False
            duplicate_headers_found = False
            
            for record in SeqIO.parse(input_fasta, "fasta"):
                header = record.id
                if any(base not in "ACTGNactgn" for base in record.seq):
                    print(f"Error: Invalid nucleotide characters found in {input_assembly_file} for sequence {record.id}\n")
                    invalid_chars_found = True
                if header in headers_seen:
                    print(f"Error: Duplicate header found in {input_assembly_file}: {header}\n")
                    duplicate_headers_found = True
                headers_seen.add(header)
            
            if invalid_chars_found or duplicate_headers_found:
                sys.exit(1)

    print("The input assembly files look fine. Proceeding to the next steps.")

def create_output_folders(args):
    print(f"\n\033[1m{print_step(create_output_folders)}: Creating MVP directories where outputs will be stored...\033[0m")

    output_folders = ['00_DATABASES', '01_GENOMAD', '02_CHECK_V', '03_CLUSTERING', '04_READ_MAPPING', '05_VOTU_TABLES', '06_FUNCTIONAL_ANNOTATION']
    for folder_name in output_folders:
        output_folder = os.path.join(args["input"], folder_name)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

def install_databases(args):
    if args["skip_install_databases"]:
        genomad_db_path = None
        checkv_db_path = None
        print(f"\n\033[1m{print_step(install_databases)}: Skipping to install databases because --install_databases is False...\033[0m")
    else:
        database_path = os.path.join(args["input"], '00_DATABASES')
        os.makedirs(database_path, exist_ok=True)

        # Install geNomad database
        if args['genomad_db_path']:
            genomad_db_path = os.path.join(args['genomad_db_path'], 'genomad_db')
        else:
            genomad_db_path = os.path.join(database_path, 'genomad_db')
        
        if os.path.exists(genomad_db_path):
            print(f"\n\033[1m{print_step(install_databases)}: Skipping to install geNomad database because {genomad_db_path} already exists...\033[0m")
        else:
            print(f"\n\033[1m{print_step(install_databases)}: Creating geNomad database...\033[0m")
            subprocess.run(['genomad', 'download-database', database_path])

        # Install CheckV database
        if args['checkv_db_path']:
            checkv_db_path = os.path.join(args['checkv_db_path'], 'checkv-db-v1.5')
        else:
            checkv_db_path = os.path.join(database_path, 'checkv-db-v1.5')

        if os.path.exists(checkv_db_path):
            print(f"\n\033[1m{print_step(install_databases)}: Skipping to install Check_V database because {checkv_db_path} already exists...\033[0m")
        else:
            print(f"\n\033[1m{print_step(install_databases)}: Creating CheckV database...\033[0m")
            subprocess.run(['checkv', 'download_database', database_path])

        additional_dbs = ['PhrogDB_v14', 'RdRP_DB', 'Pfam_A_DB', 'dbAPIS']
        for db in additional_dbs:
            db_path = os.path.join(database_path, db)
            if os.path.exists(db_path) and os.listdir(db_path):
                print(f"\n\033[1m{print_step(install_databases)}: Skipping install of {db} because it already exists...\033[0m")
            else:
                print(f"\n\033[1m{print_step(install_databases)}: Downloading {db}...\033[0m")
                subprocess.run(['wget', '-r', '-np', '-nH', '--cut-dirs=3', '--reject="index.html*"', f'https://portal.nersc.gov/cfs/m342/MViP/{db}/', '-P', database_path])

    return genomad_db_path, checkv_db_path

def generate_summary_report(args, genomad_db_path, checkv_db_path, formatted_start_time, formatted_end_time, duration):
    print(f"\n\033[1m{print_step(generate_summary_report)}: Generating summary report for Module 00...\033[0m")

    # Create a dictionary to hold argument descriptions and their default values
    argument_defaults = {
        '--input': args["input"],
        '--metadata': args["metadata"],
        '--skip_check_errors': args["skip_check_errors"],
        '--skip_install_databases': args["skip_install_databases"],
        '--genomad_db_path': genomad_db_path,
        '--checkv_db_path': checkv_db_path
    }

    # Create the module header
    module_header = """
****************************************************************************
*********                          MODULE 00                       *********
****************************************************************************
"""

    # Write a summary line with script arguments and their default values
    summary_line = "00_set_up_mvp.py"
    for arg, default in argument_defaults.items():
        if default is not None:
            summary_line += f" {arg} {default}"

    # Create a summary report file
    summary_report_path = os.path.join(args["input"], 'MVP_00_Summary_Report.txt')

    with open(summary_report_path, 'w') as summary_report:
        # Write the module header
        summary_report.write(module_header.strip() + '\n')
        summary_report.write(summary_line + '\n\n')
        summary_report.write(f"Start Time: {formatted_start_time}\n")
        summary_report.write(f"End Time: {formatted_end_time}\n")
        summary_report.write(f"Running Time: {duration.total_seconds():.2f} seconds\n\n")
        summary_report.write("Tools and versions:\n")

        # List of tools
        tools = [
            "tqdm", "genomad", "pandas", "checkv", "bowtie2", "minimap2", 
            "samtools", "seqtk", "scikit-learn", "numpy", "parallel", 
            "coverm", "python", "dos2unix", "mmseqs2", "mafft", "trimal", 
            "fasttree", "vRhyme", "taxopy", "table2asn"
        ]

        # Define a list of package managers to try
        package_managers = ["conda", "mamba", "micromamba"]

        # For each tool, try finding its version using each package manager
        for tool in tools:
            found_version = False
            for manager in package_managers:
                try:
                    result = subprocess.run(
                        [manager, "list", tool], capture_output=True, text=True, check=True
                    )
                    lines = result.stdout.splitlines()
                    if len(lines) > 3:
                        version_line = lines[3]  # Assuming the version info is in the 4th line
                        version = version_line.split()[1]
                        summary_report.write(f"{tool} {version}\n")
                        found_version = True
                        break
                except subprocess.CalledProcessError:
                    continue
                except FileNotFoundError:
                    continue  # Skip to the next package manager if the current one isn't found

            if not found_version:
                summary_report.write(f"{tool} version not found\n")

        # Add section for databases and versions
        summary_report.write("\nDatabases and versions:\n")
        if genomad_db_path:
            genomad_db_name = os.path.basename(genomad_db_path)
            # Read version from version.txt
            version_file_path = os.path.join(genomad_db_path, 'version.txt')
            if os.path.exists(version_file_path):
                with open(version_file_path, 'r') as version_file:
                    genomad_version = version_file.read().strip()
                summary_report.write(f"{genomad_db_name} {genomad_version}\n")
            else:
                summary_report.write(f"{genomad_db_name}: version file not found\n")
        else:
            summary_report.write("geNomad database: not installed\n")
        
        if checkv_db_path:
            checkv_db_name = os.path.basename(checkv_db_path)
            # Extract version number from checkv_db_path
            checkv_version = checkv_db_name.split('-')[-1].replace('v', '')
            summary_report.write(f"{checkv_db_name} {checkv_version}\n")
        else:
            summary_report.write("CheckV database: not installed\n")

    print("Summary report for Module 00 has been created:", summary_report_path)

def main(args):
    # Capture start time
    start_time = datetime.datetime.now()
    formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S") 
    print(f"\nStart Time: {formatted_start_time}")

    # Usage of run_step for the dos2unix step
    convert_metadata_to_unix(args)

    check_metadata(args)

    # Usage of run_step for the check_paths step
    check_paths(args)

    # Usage of run_step for the check_sequence_data step
    check_sequence_data(args)

    create_output_folders(args)

    genomad_db_path, checkv_db_path = install_databases(args)

    # Capture end time
    end_time = datetime.datetime.now()
    formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate duration
    duration = end_time - start_time

    # Add this function to your script
    generate_summary_report(args, genomad_db_path, checkv_db_path, formatted_start_time, formatted_end_time, duration)

    message1 = "\033[1mModule 00 finished: you are all set to use MVP!\n\033[0m"
    message2 = "Your metadata looks fine, as well as your read and assembly files."
    message3 = "All the directories needed for MVP have been generated in your working directory."
    if not args["skip_install_databases"]:
        message4 = "geNomad and CheckV databases have been installed in their respective directories."
    message5 = "\n\033[1mYou can now proceed to the next step of the MVP script: Module 01!\033[0m"
    line_of_stars = '*' * len(message3)

    print()
    print(line_of_stars)
    print(message1)
    print(f"Start Time: {formatted_start_time}")
    print(f"End Time: {formatted_end_time}")
    print(f"Running Time: {duration.total_seconds():.2f} seconds\n")
    print(message2)
    print(message3)
    if not args["skip_install_databases"]:
        print(message4)
    print(message5)
    print(line_of_stars)
    print()

    print("Please don't forget to cite MVP and the following softwares used in this module:")
    print("- Camargo, A. P., Roux, S., Schulz, F., Babinski, M., Xu, Y., Hu, B., Chain, P. S. G., Nayfach, S., & Kyrpides, N. C. You can move, but you can’t hide: identification of mobile genetic elements with geNomad. bioRxiv (2023), DOI: 10.1101/2020.11.01.361691")
    print("\n- Nayfach, S., Camargo, A.P., Schulz, F. et al. CheckV assesses the quality and completeness of metagenome-assembled viral genomes. Nat Biotechnol 39, 578–585 (2021). https://doi.org/10.1038/s41587-020-00774-7\n")
