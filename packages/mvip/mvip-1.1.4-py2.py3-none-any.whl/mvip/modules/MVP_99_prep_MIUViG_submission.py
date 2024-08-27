import argparse
import glob
import os
import subprocess
import sys
import csv
import shutil
import subprocess as sp
import datetime
import time
from os.path import getsize
import pandas as pd
from functools import reduce
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import mvip

def fetch_arguments(parser):
    parser.set_defaults(func=main)
    parser.set_defaults(program="MVP_99_prep_MIUViG_submission")
    parser.add_argument(
        "--input", "-i",
        help="Path to your working directory where you want to run MVP.",
    )
    parser.add_argument(
        "--metadata", "-m",
        help="Path to your metadata that you want to use to run MVP.",
    )
    parser.add_argument('-g', '--genome', help='Identifier of the sequence to be processed.', required=True)
    parser.add_argument('-s', '--step', help='Should be one of "setup_metadata" (to be run first) or "prep_submission" (once sequence metadata have been checked and completed).', choices=['setup_metadata', 'prep_submission'], required=True)
    parser.add_argument('-t', '--template', help='path to the BioSample submission template file, generated from https://submit.ncbi.nlm.nih.gov/genbank/template/submission/, only required for the step 2: prep_submission', required=False)


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


# Prep a quick function to load only some specific sequences from a fasta file, may be useful in multiple places
def load_seq(in_fasta,list_ids):
    seq_return = {}
    for seq_record in SeqIO.parse(in_fasta, "fasta"):
        if seq_record.id in list_ids:
            seq_return[seq_record.id] = seq_record.seq

    return seq_return

def create_output_directory(args):
    # prep the output directory if needed
    r_dir = os.path.join(args['input'], '99_GENBANK_SUBMISSION')
    tpl_dir = os.path.join(args['input'], '99_GENBANK_SUBMISSION', 'UViG_metadata_tables/')
    sub_dir = os.path.join(args['input'], '99_GENBANK_SUBMISSION', 'UViG_submission_files/')
    if not os.path.exists(r_dir):
        os.makedirs(r_dir)
    if not os.path.exists(tpl_dir):
        os.makedirs(tpl_dir)
    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir)

    return tpl_dir, sub_dir

def create_template_path():
    # Construct the path to the template files
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # Get the directory of the mvp directory
    mvp_directory = os.path.dirname(script_directory)
    data_directory = os.path.join(mvp_directory, "data")
    template_metadata = os.path.join(data_directory, "miuvig_template-custom.txt")

    return template_metadata

def load_files(args, tpl_dir):
    # Path for output files:
    out_metadata = os.path.join(tpl_dir, args['genome'] + "_metadata.tsv")
    out_annotation = os.path.join(tpl_dir, args['genome'] + "_annotation.tsv")
    # Load sample metadata
    metadata = pd.read_csv(args['metadata'], sep='\t')
    # Load list of sequences
    summary_file = os.path.join(args['input'], '03_CLUSTERING', 'MVP_03_All_Sample_Unfiltered_Merged_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv')
    seq_summary = pd.read_csv(summary_file, sep='\t')

    return out_metadata, out_annotation, metadata, summary_file, seq_summary

# Prep the functions we need for that
def add_gene(vec,o, seq_summary):
    if vec["strand"] == -1:
        if vec['start'] < 3:
            o.write(f"{vec['end']}\t>1\tCDS\n") ## Right now assuming that a gene ending on the edge is likely to be partial, should be better though because there is a small but not impossible chance of a gene ending right on the edge, we'll see if this causes issues down the road
        else:
            o.write(f"{vec['end']}\t{vec['start']}\tCDS\n")
    else:
        if vec['end'] > (seq_summary["virus_length"]-3):
            o.write(f"{vec['start']}\t>{vec['end']}\tCDS\n")
    o.write(f"\t\t\tcodon_start\t1\n")
    o.write(f"\t\t\tinference\tab initio prediction:Prodigal-gv\n")
    o.write(f"\t\t\tlocus_tag\t{vec['Viral_gene_ID']}\n")
    if vec['GENOMAD_Annotation'] == "Unknown":
        vec['GENOMAD_Annotation'] = "hypothetical protein"
    o.write(f"\t\t\tproduct\t{vec['GENOMAD_Annotation']}\n")

def set_up_metadata(args, seq_summary, summary_file, metadata, template_metadata, out_metadata, out_annotation, tpl_dir):
    print(f"\033[1m{step_counter.print_main_step()}: Selecting the corresponding line, exiting if can't find it...\033[0m")
    seq_summary = seq_summary[seq_summary["virus_id"] == args['genome']]
    if len(seq_summary) != 1:
        if len(seq_summary) == 0:
            sys.exit(f"ERROR - We could not find {args['genome']} in {summary_file}, please double check that the genome id you provided is correct")
        elif len(seq_summary) > 1:
            sys.exit(f"ERROR - We expected to select a single row based on {args['genome']}, but we got more than one, please double check")
    seq_summary = seq_summary.squeeze()
    # Throw a warning if low-quality, not recommended
    if seq_summary["checkv_quality"] == "Low-quality":
        print("")
        print("WARNING - the sequence selected was predicted to be a partial genome of low quality, it is typically not recommended to submit these low-quality sequences to public databases")
        print("Press Enter to continue or q to stop")
        test = input()
        if test == "q" or test == "Q":
            sys.exit()

    print(f"\n\033[1m{step_counter.print_main_step()}: Load the version information for each database and tool...\033[0m")
    version_file = os.path.join(args['input'], "MVP_00_Summary_Report.txt")
    info_version = {}
    with open(version_file,"r") as f:
        tag = 0
        for line in f.readlines():
            line = line.strip()
            if line.startswith("Tools and versions:"):
                tag = 1
            elif tag == 1:
                t = line.split(" ")
                info_version[t[0]] = t[1]
            elif line.startswith(" "):
                tag = 0

    print(f"\n\033[1m{step_counter.print_main_step()}: Guessing the sample id for this sequence...\033[0m")
    info_analysis = {}
    for row_index, (_, row) in enumerate(metadata.iterrows(), start=1):
        sample_name = row['Sample']
        test_file = os.path.join(args['input'], '02_CHECK_V', str(sample_name), 'MVP_02_' + str(sample_name) + '_Filtered_Relaxed_Merged_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv')
        test_df = pd.read_csv(test_file, sep='\t')
        if args['genome'] in test_df["virus_id"].values:
            print(f"genome {args['genome']} was obtained from sample {sample_name}")
            seq_summary["sample"] = sample_name
            ## Add other info if needed
            test_df =  test_df[test_df["virus_id"] == args['genome']].squeeze()
            seq_summary["provirus"] = test_df["provirus"]
            seq_summary["name"] = args['genome']
            tax_tab = test_df["taxonomy"].split(";")
            ## taxonomy -> used for organism and lineage
            if len(tax_tab) > 0:
                seq_summary["organism"] = tax_tab[-1] + " sp. " + args['genome']
            else:
                seq_summary["organism"] = "unclassified virus"
            seq_summary["lineage"] = test_df["taxonomy"]
            seq_summary["virus_length"] = test_df["virus_length"]
            ## genetic code automatically selected by geNomad
            seq_summary["gcode"] = test_df["genetic_code"]
            # Load topology information from geNomad
            step_one_result_one_path = os.path.join(args['input'], '01_GENOMAD', str(sample_name), str(sample_name) + '_Viruses_Genomad_Output', '*_summary', '*_virus_summary.tsv')
            step_one_result_one_file = glob.glob(step_one_result_one_path)
            step_one_result_one_file = step_one_result_one_file[0]
            test_df = pd.read_csv(step_one_result_one_file, sep='\t')
            test_df =  test_df[test_df["seq_name"] == args['genome']].squeeze() ## Should be a scalar now, because it should be a single line per genome
            seq_summary["topology"] = "linear"
            # if test_df["topology"].isin(["DTR"]).any():
            if test_df["topology"] == "DTR":
                seq_summary["topology"] = "circular"
            # Load information about identification
            info_analysis["id_tool"] = "geNomad" ## Setup defaults just in case
            info_analysis["id_version"] = info_version["genomad"]
            info_analysis["check_tool"] = "CheckV"
            info_analysis["check_version"] = info_version["checkv"]
            # Detailed completeness
            comp_file_one = os.path.join(args['input'], '02_CHECK_V', str(sample_name), str(sample_name) + '_Viruses_CheckV_Output', 'completeness.tsv')
            if os.path.exists(comp_file_one):
                comp_df = pd.read_csv(comp_file_one, sep='\t')
                if args['genome'] in comp_df["contig_id"].values:
                    comp_df = comp_df[comp_df["contig_id"] == args['genome']].squeeze()
                    if comp_df["aai_confidence"] == "high" or comp_df["aai_confidence"] == "medium":
                        seq_summary["compl_appr"] = "reference-based"
                        seq_summary["compl_score"] = comp_df["aai_completeness"]
                        seq_summary["estimated_size"] = int(comp_df["aai_expected_length"])
            comp_file_two = os.path.join(args['input'], '02_CHECK_V', str(sample_name), str(sample_name) + '_Proviruses_CheckV_Output', 'completeness.tsv')
            if os.path.exists(comp_file_two):
                comp_df = pd.read_csv(comp_file_one, sep='\t')
                if args['genome'] in comp_df["contig_id"].values:
                    comp_df = comp_df[comp_df["contig_id"] == args['genome']].squeeze()
                    if comp_df["aai_confidence"] == "high" or comp_df["aai_confidence"] == "medium":
                        seq_summary["compl_appr"] = "reference-based"
                        seq_summary["compl_score"] = comp_df["aai_completeness"]
                        seq_summary["estimated_size"] = int(comp_df["aai_expected_length"])

    print(f"\n\033[1m{step_counter.print_main_step()}: Loading information about vOTU clustering, and making sure this sequence is a representative...\033[0m")
    seq_summary["otu_seq_comp_appr"] = info_analysis["check_tool"] + " clustering;" + str(info_analysis["check_version"])
    step_three_report = os.path.join(args['input'], '03_CLUSTERING', 'MVP_03_Summary_Report.txt')
    with open(step_three_report,"r") as f:
        tmp = {}
        for line in f.readlines():
            line = line.strip()
            if line.startswith("03_do_clustering.py"):
                t = line.split(" ")
                for i in range(len(t)):
                    if t[i] == "--min_ani":
                        tmp["ani"] = t[i+1]
                    if t[i] == "--min_tcov":
                        tmp["af"] = t[i+1]
        if tmp["ani"] != "" and tmp["af"] != "":
            seq_summary["otu_class_appr"] = str(tmp["ani"]) + "% ANI;" + str(tmp["af"]) + "% AF; greedy incremental clustering"
    step_three_result = os.path.join(args['input'], '03_CLUSTERING', 'tmp', 'MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences_Clustering_ANI_Clusters.tsv')
    with open(step_three_result,"r") as f:
        tmp = {}
        for line in f.readlines():
            line = line.strip()
            t = line.split("\t")
            list = t[1].split(",")
            if args['genome'] == t[0]:
                seq_summary["repr"] = t[0]
            elif args['genome'] in list:
                print("")
                print(f"WARNING - THE SEQUENCE YOU SELECTED WAS NOT A vOTU REPRESENTATIVE, YOU PROBABLY WANT TO CHANGE THIS AND PICK THE REPRESENTATIVE ({t[0]}) INSTEAD")
                print("Press Enter to continue or q to stop")
                test = input()
                if test == "q" or test == "Q":
                    sys.exit()
                seq_summary["repr"] = t[0]

    print(f"\n\033[1m{step_counter.print_main_step()}: Loading information from coverage...\033[0m")
    step_four_result = os.path.join(args['input'], '04_READ_MAPPING', str(sample_name), str(sample_name) + '_CoverM.tsv')
    if os.path.exists(step_four_result):
        with open(step_four_result,"r") as f:
            for line in f.readlines():
                line = line.strip()
                if t[1] == seq_summary["repr"]:
                    seq_summary["coverage"] = "{:.2f}".format(t[3])
                    # Coverage is used in two places, formatting the one for Assembly-Data
                    seq_summary["Genome Coverage"] = seq_summary["coverage"] + "x"
    else:
        print("")
        print(f"WARNING - No coverage information found for sample {sample_name}, you will need to enter the coverage manually (we recommend looking at column 'Trimmed Mean' in the CoverM output in step 4 for your sample of interest) ")
        print("Press Enter to continue or q to stop")
        test = input()
        if test == "q" or test == "Q":
            sys.exit()
        seq_summary["coverage"] = ""
        seq_summary["Genome Coverage"] = ""

    print(f"\n\033[1m{step_counter.print_main_step()}: Reformatting the field that need it...\033[0m")
    seq_summary["completedness"] = "partial" ## Regardless of contigs topology, guidelines are that completedness for GenBank should be partial until completeness was experimentally verified
    seq_summary["metagenomic"] = "TRUE"
    seq_summary["environmental_sample"] = "TRUE"
    ## detec_type
    if seq_summary["provirus"] == "Yes":
        seq_summary["detec_type"] = "provirus (UpViG)"
        seq_summary["topology"] = "linear"
    else:
        seq_summary["detec_type"] = "independent sequence (UViG)"
    # assembly_qual
    if seq_summary["miuvig_quality"] == "High-quality":
        seq_summary["assembly_qual"] = seq_summary["miuvig_quality"] + " draft genome"
    elif seq_summary["checkvg_quality"] == "Medium-quality":
        seq_summary["assembly_qual"] = seq_summary["Medium-quality"] + " draft genome"
    else:seq_summary["assembly_qual"] = "Low-quality draft genome"
    # number_contig
    seq_summary["number_contig"] = 1 ## Note: could be modified later if we want to accomdate bins, e.g. from vRhyme
    # pred_genome_struc
    seq_summary["pred_genome_struc"] = "non-segmented" ## NOTE - THIS SHOULD BE FINE MOST OF THE TIME, BUT COULD BE REFINED BASED ON TAXONOMY !
    # pred_genome_type
    seq_summary["pred_genome_type"] = seq_summary["Genome type"]
    # softwares used for identification, completeness, and taxonomy
    seq_summary["vir_ident_software"] = info_analysis["id_tool"] + ";" + str(info_analysis["id_version"]) + ";" + str(seq_summary["virus_score"])
    seq_summary["compl_software"] = info_analysis["check_tool"] + ";" + str(info_analysis["check_version"])
    seq_summary["tax_class"] = info_analysis["id_tool"] + ";" + str(info_analysis["id_version"])
    seq_summary["tax_ident"] = "multi-marker approach" ## geNomad, by default a multi-marker approach
    # feat_pred and similar annotation questions
    seq_summary["annot"] = "geNomad" + ";" + info_version["genomad"] ## Features predicted from geNomad
    seq_summary["feat_pred"] = "prodigal-gv;geNomad" + info_version["genomad"] ## Features predicted from geNomad
    seq_summary["ref_db"] = "Pfam" ## Features predicted from geNomad
    seq_summary["sim_search_meth"] = "mmseqs2" + ";" + info_version["mmseqs2"]
    print("We loaded all the data we wanted, now we create the first metadata and annotation files")

    print(f"\n\033[1m{step_counter.print_main_step()}: Read the template and write the output file with genome-specific information...\033[0m")
    with open(template_metadata,"r") as f, open(out_metadata,"w") as o:
        tmp = {}
        freader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        mwriter = csv.writer(o, delimiter='\t',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in freader:
            if len(row) > 0:
                if row[0].startswith("#"):
                    row[1] = args['genome']
                elif row[0] != "":
                    if row[0] in seq_summary:
                        row[1] = seq_summary[row[0]]
            mwriter.writerow(row)

    print(f"\n\033[1m{step_counter.print_main_step()}: Creating the annotation file we will need based on the gene annotation by geNomad...\033[0m")
    annotation_file = os.path.join(args['input'], '06_FUNCTIONAL_ANNOTATION', 'MVP_06_All_Sample_Filtered_Relaxed_Merged_Genomad_CheckV_Virus_Proviruses_Gene_Annotation_GENOMAD.tsv')
    annot_df = pd.read_csv(annotation_file, sep='\t')
    annot_df =  annot_df[annot_df["Contig_name"] == args['genome']]
    with open(out_annotation,"w") as o:
        o.write(">Feature "+args['genome']+"\n")
        annot_df.apply(lambda x: add_gene(x,o, seq_summary), axis=1)

def prep_submission(args, out_metadata, out_annotation, sub_dir):
    print(f"\n\033[1m{step_counter.print_main_step()}: Checking that all the required files are here...\033[0m")
    out_fasta = os.path.join(sub_dir, args['genome'] + "_genome.fna")
    clean_metadata = os.path.join(sub_dir, args['genome'] + "_comments.cmt")
    final_annotation = os.path.join(sub_dir, args['genome'] + "_genome.tbl")
    template_file = args['template']
    if not(os.path.exists(out_metadata)):
        sys.exit(f"{out_metadata} does not seem to exist, please run step 'setup_metadata' first")
    if not(os.path.exists(out_annotation)):
        sys.exit(f"{out_annotation} does not seem to exist, please run step 'setup_metadata' first")
    if template_file == None or not(os.path.exists(template_file)):
        sys.exit(f"Please provide a path for a template file with the argument '-t' for this submission (see https://submit.ncbi.nlm.nih.gov/genbank/template/submission/)")
    if not(os.path.exists(template_file)):
        sys.exit(f"Template file {template_file} does not seem to exist, please generate a BioSample template file for this submission (see https://submit.ncbi.nlm.nih.gov/genbank/template/submission/), and provide it with the argument '--template'")

    print(f"\n\033[1m{step_counter.print_main_step()}: Loading metadata and check that all the required information is entered...\033[0m")
    tmp_metadata = {}
    with open(out_metadata,"r") as f:
        freader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        for row in freader:
            if len(row) > 1:
                if row[1] != "":
                    tmp_metadata[row[0]] = row[1]
                elif len(row) > 2 and row[2] == "yes":
                    sys.exit(f"{row[0]} is a required field, please complete the file {out_metadata} and re-run this step")

    print(f"\n\033[1m{step_counter.print_main_step()}: Preparing input for table2asn...\033[0m")
    list_ids = [args['genome']]
    in_fasta = os.path.join(args['input'], '03_CLUSTERING/', 'MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences.fna')
    seq_genome = load_seq(in_fasta,list_ids)
    combined_description = f"[organism={tmp_metadata['organism']}]"
    combined_description = combined_description + f" [topology={tmp_metadata['topology']}]"
    combined_description = combined_description + f" [gcode={tmp_metadata['gcode']}]"
    combined_description = combined_description + f" [completedness={tmp_metadata['completedness']}]"
    combined_description = combined_description + f" [moltype={tmp_metadata['moltype']}]"
    combined_description = combined_description + f" [lat_lon=\"{tmp_metadata['lat_lon']}\"]"
    combined_description = combined_description + f" [collection_date={tmp_metadata['collection_date']}]"
    combined_description = combined_description + f" [metagenomic={tmp_metadata['metagenomic']}]"
    combined_description = combined_description + f" [environmental_sample={tmp_metadata['environmental_sample']}]"
    combined_description = combined_description + f" [isolation source=\"{tmp_metadata['geo_loc_name']}\"]"
    if "host" in tmp_metadata:
        combined_description = combined_description + f" [host={tmp_metadata['host']}]"
    if "sra_reads" in tmp_metadata:
        combined_description = combined_description + f" [note=genome assembled from reads in {tmp_metadata['sra_reads']}]"
    with open(out_fasta, "w") as output_handle:
        seq_record = SeqRecord(
            seq_genome[args['genome']],
            id=args['genome'],
            description=combined_description)
        SeqIO.write(seq_record, output_handle, "fasta")

    print(f"\n\033[1m{step_counter.print_main_step()}: Creating a clean version of the metadata...\033[0m")
    with open(out_metadata,"r") as f, open(clean_metadata,"w") as o:
        tag = 0
        tmp = {}
        freader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        mwriter = csv.writer(o, delimiter='\t',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in freader:
            if len(row) > 1 and row[1] != "":
                if row[0].startswith("StructuredCommentPrefix"):
                    tag = 1
                if tag == 1 and not(row[0].startswith("#")):
                    mwriter.writerow(row[0:2])
                    # print(f"{row[0]}\t{row[1]}")
                    if row[0] == "StructuredCommentPrefix" and row[1] == "Assembly-Data":
                        tab_asbly = tmp_metadata["assembly_software"].split(";")
                        reformat_asbly = tab_asbly[0] + " " + tab_asbly[1]
                        mwriter.writerow(["Assembly Method",reformat_asbly])

    # Finally copying over the annotation with the right file name so that it's picked up by table2asn
    shutil.copyfile(out_annotation, final_annotation)

    print(f"\n\033[1m{step_counter.print_main_step()}: Preparing to run table2asn as follows...\033[0m")
    cmd = f"table2asn -i {out_fasta} -w {clean_metadata} -t {template_file} -a s -V vb -Z "
    print(f"{cmd}")
    p = sp.Popen(cmd, shell=True)
    p.wait()
    # Testing if we have any error and reportin them here if we do
    print("##########################################################\n")
    print("List of warning / information reported by table2asn -- these are just for your information:")
    error_file = os.path.join(sub_dir, args['genome'] + "_genome.val")
    with open(error_file,"r") as f:
        for line in f.readlines():
            if line.startswith("Warning") or line.startswith("Info"):
                print(f"{line}")
    print("##########################################################\n")
    print("Checking for any errors reported by table2asn -- these would be important to fix before submission to NCBI:")
    error_file = os.path.join(sub_dir, args['genome'] + "_genome.val")
    tag = 0
    with open(error_file,"r") as f:
        for line in f.readlines():
            if not(line.startswith("Warning")) and not(line.startswith("Info")):
                print(f"UNEXPECTED ERROR -- {line}")
                tag = 1
    if tag == 0:
        print("MVP did not notice any major error here, that's great ! ")
    print("\n##########################################################\n\n")
    sqn_file = os.path.join(sub_dir, args['genome'] + "_genome.sqn")
    gb_file = os.path.join(sub_dir, args['genome'] + "_genome.gb")

    return sqn_file, gb_file



def main(args):
    # Capture start time
    start_time = datetime.datetime.now()
    formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nStart Time: {formatted_start_time}\n")

    tpl_dir, sub_dir = create_output_directory(args)

    template_metadata = create_template_path()

    out_metadata, out_annotation, metadata, summary_file, seq_summary = load_files(args, tpl_dir)

    # If step = setup_metadata
    if args['step'] == "setup_metadata":
        set_up_metadata(args, seq_summary, summary_file, metadata, template_metadata, out_metadata, out_annotation, tpl_dir)

        # Capture end time
        end_time = datetime.datetime.now()
        formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

        # Calculate duration
        duration = end_time - start_time

        message1 = "\033[1mModule 99 finished: Submission files generated!\033[0m\n"
        line_of_stars = '*' * len(message1)
        print()
        print(line_of_stars)
        print(message1)
        print(f"Start Time: {formatted_start_time}") 
        print(f"End Time: {formatted_end_time}")
        print(f"Running Time: {duration.total_seconds():.2f} seconds\n")
        print(f"The files were created in {tpl_dir}, the next step is for you to review and complete the information in {out_metadata}")
        print(f"In particular, make sure that all rows noted as 'yes' in the 'required' column are filled in, and review (and modify if needed) all the rows pre-filled by MVP")
        print(f"Once this is done, you should run the step 'prep_submission' for the same genome, i.e. ")
        print(f"99_prep_MIUViG_submission.py -s prep_submission -t /path/to/sample/template.sbt -i {args['input']} -m {args['metadata']} -g {args['genome']}")
        print(line_of_stars)
        print()


    # If step = prep_submission
    if args['step'] == "prep_submission":
        sqn_file, gb_file = prep_submission(args, out_metadata, out_annotation, sub_dir)

        # Capture end time
        end_time = datetime.datetime.now()
        formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

        # Calculate duration
        duration = end_time - start_time

        message1 = "\033[1mModule 99 finished: Submission files generated!\033[0m\n"
        line_of_stars = '*' * len(message1)
        print()
        print(line_of_stars)
        print(message1)
        print(f"Start Time: {formatted_start_time}") 
        print(f"End Time: {formatted_end_time}")
        print(f"Running Time: {duration.total_seconds():.2f} seconds\n")
        print("Submission files generated, if you had some 'ERROR -- error' reported above, please correct the input files manually and re-run the prep_submission step or just table2asn using the command line listed above")
        print(f"To check the final annotated file, you can use {gb_file} in a genome browser")
        print(f"This GenBank file should include all the right information in the header, the MIUViG-formatted metadata as a formatted comment, and the gene annotation generated by geNomad")
        print(f"For final submission, you can use {sqn_file}")
        print(line_of_stars)
        print()
