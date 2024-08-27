"""
MVP: Modular Viromics Pipeline for studying viruses identified from sequencing data
"""

from mvip.modules import (
    MVP_00_set_up_MVP,
    MVP_01_run_genomad_checkv,
    MVP_02_filter_genomad_checkv,
    MVP_03_do_clustering,
    MVP_04_do_read_mapping,
    MVP_05_create_vOTU_table,
    MVP_06_do_functional_annotation,
    MVP_07_do_binning,
    MVP_99_prep_MIUViG_submission,
    MVP_100_summarize_outputs,
)

__version__ = "1.1.4"
