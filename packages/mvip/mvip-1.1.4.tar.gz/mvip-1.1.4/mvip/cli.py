import argparse
import sys
import mvip

def cli():
    parser = argparse.ArgumentParser(
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f"""MVP v{mvip.__version__}: assessing the quality of metagenome-assembled viral genomes
https://gitlab.com/ccoclet/mvp

usage: mvip <program> [options]

programs:
    MVP_00_set_up_MVP                   Check for any potential errors/issues in the metadata and the sequencing/read files, create all the directories that MVP needs, and install the latest versions of geNomad and checkV databases.
    MVP_01_run_genomad_checkv           Run geNomad and CheckV.
    MVP_02_filter_genomad_checkv        Merge and filter geNomad and CheckV outputs.
    MVP_03_do_clustering                Sequence clustering based on pairwise ANI.
    MVP_04_do_read_mapping              Run CoverM to calculate coverage based on read mapping, using the sorted BAM files sorted by reference, and return to one tabular file per sample.
    MVP_05_create_vOTU_table            Merge all the CoverM output tables and create a set of viral OTU tables based on the cutoffs (i.e., horizontal coverage) and filtration mode (i.e., conservative and relaxed).
    MVP_06_do_functional_annotation     Functional annotation of protein sequences against multiple databases.
    MVP_07_do_binning                   Run vRhyme for binning virus genomes and return outputs.
    MVP_99_prep_MIUViG_submission       Additional module to assist with submitting metagenome-assembled viral genome(s) to GenBank, including MIUViG metadata.
    MVP_100_summarize_outputs           Summarize outputs and create figures.""",
    )

    subparsers = parser.add_subparsers(help=argparse.SUPPRESS)

    MVP_00_set_up_MVP_parser = subparsers.add_parser(
        "MVP_00_set_up_MVP",
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Check for any potential errors/issues in the metadata and the sequencing/read files, create all the directories that MVP needs, and install the latest versions of geNomad and checkV databases.
\nusage: mvip MVP_00_set_up_MVP -i <working_directory_path> -m <metadata_path> [options]""",
    )
    mvip.MVP_00_set_up_MVP.fetch_arguments(MVP_00_set_up_MVP_parser)

    MVP_01_run_genomad_checkv_parser = subparsers.add_parser(
        "MVP_01_run_genomad_checkv",
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Run geNomad and CheckV.
\nusage: mvip MVP_01_run_genomad_checkv -i <working_directory_path> -m <metadata_path> [options]""",
    )
    mvip.MVP_01_run_genomad_checkv.fetch_arguments(MVP_01_run_genomad_checkv_parser)

    MVP_02_filter_genomad_checkv_parser = subparsers.add_parser(
        "MVP_02_filter_genomad_checkv",
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Merge and filter geNomad and CheckV outputs.
\nusage: mvip MVP_02_filter_genomad_checkv -i <working_directory_path> -m <metadata_path> [options]""",
    )
    mvip.MVP_02_filter_genomad_checkv.fetch_arguments(MVP_02_filter_genomad_checkv_parser)

    MVP_03_do_clustering_parser = subparsers.add_parser(
        "MVP_03_do_clustering",
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Sequence clustering based on pairwise ANI.
\nusage: mvip MVP_03_do_clustering -i <working_directory_path> -m <metadata_path> [options]""",
    )
    mvip.MVP_03_do_clustering.fetch_arguments(MVP_03_do_clustering_parser)

    MVP_04_do_read_mapping_parser = subparsers.add_parser(
        "MVP_04_do_read_mapping",
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Run CoverM to calculate coverage based on read mapping, using the sorted BAM files sorted by reference, and return to one tabular file per sample.
\nusage: mvip MVP_04_do_read_mapping -i <working_directory_path> -m <metadata_path> [options]""",
    )
    mvip.MVP_04_do_read_mapping.fetch_arguments(MVP_04_do_read_mapping_parser)

    MVP_05_create_vOTU_table_parser = subparsers.add_parser(
        "MVP_05_create_vOTU_table",
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Merge all the CoverM output tables and create a set of viral OTU tables based on the cutoffs (i.e., horizontal coverage) and filtration mode (i.e., conservative and relaxed).
\nusage: mvip MVP_05_create_vOTU_table -i <working_directory_path> -m <metadata_path> [options]""",
    )
    mvip.MVP_05_create_vOTU_table.fetch_arguments(MVP_05_create_vOTU_table_parser)

    MVP_06_do_functional_annotation_parser = subparsers.add_parser(
        "MVP_06_do_functional_annotation",
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Functional annotation of protein sequences against multiple databases.
\nusage: mvip MVP_06_do_functional_annotation -i <working_directory_path> -m <metadata_path> [options]""",
    )
    mvip.MVP_06_do_functional_annotation.fetch_arguments(MVP_06_do_functional_annotation_parser)

    MVP_07_do_binning_parser = subparsers.add_parser(
        "MVP_07_do_binning",
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Run vRhyme for binning virus genomes and return outputs.
\nusage: mvip MVP_07_do_binning -i <working_directory_path> -m <metadata_path> [options]""",
    )
    mvip.MVP_07_do_binning.fetch_arguments(MVP_07_do_binning_parser)

    MVP_99_prep_MIUViG_submission_parser = subparsers.add_parser(
        "MVP_99_prep_MIUViG_submission",
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Additional module to assist with submitting metagenome-assembled viral genome(s) to GenBank, including MIUViG metadata.
\nusage: mvip MVP_99_prep_MIUViG_submission -i <working_directory_path> -m <metadata_path> [options]""",
    )
    mvip.MVP_99_prep_MIUViG_submission.fetch_arguments(MVP_99_prep_MIUViG_submission_parser)

    MVP_100_summarize_outputs_parser = subparsers.add_parser(
        "MVP_100_summarize_outputs",
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Summarize outputs and create figures.
\nusage: mvip MVP_100_summarize_outputs -i <working_directory_path> -m <metadata_path> [options]""",
    )
    mvip.MVP_100_summarize_outputs.fetch_arguments(MVP_100_summarize_outputs_parser)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    elif len(sys.argv) == 2:
        if sys.argv[1] == "MVP_00_set_up_MVP":
            MVP_00_set_up_MVP_parser.print_help()
            sys.exit(0)
        elif sys.argv[1] == "MVP_01_run_genomad_checkv":
            MVP_01_run_genomad_checkv_parser.print_help()
            sys.exit(0)
        elif sys.argv[1] == "MVP_02_filter_genomad_checkv":
            MVP_02_filter_genomad_checkv_parser.print_help()
            sys.exit(0)
        elif sys.argv[1] == "MVP_03_do_clustering":
            MVP_03_do_clustering_parser.print_help()
            sys.exit(0)
        elif sys.argv[1] == "MVP_04_do_read_mapping":
            MVP_04_do_read_mapping_parser.print_help()
            sys.exit(0)
        elif sys.argv[1] == "MVP_05_create_vOTU_table":
            MVP_05_create_vOTU_table_parser.print_help()
            sys.exit(0)
        elif sys.argv[1] == "MVP_06_do_functional_annotation":
            MVP_06_do_functional_annotation_parser.print_help()
            sys.exit(0)
        elif sys.argv[1] == "MVP_07_do_binning":
            MVP_07_do_binning_parser.print_help()
            sys.exit(0)
        elif sys.argv[1] == "MVP_99_prep_MIUViG_submission":
            MVP_99_prep_MIUViG_submission_parser.print_help()
            sys.exit(0)
        elif sys.argv[1] == "MVP_100_summarize_outputs":
            MVP_100_summarize_outputs_parser.print_help()
            sys.exit(0)
            
    args = vars(parser.parse_args())
    args["func"](args)