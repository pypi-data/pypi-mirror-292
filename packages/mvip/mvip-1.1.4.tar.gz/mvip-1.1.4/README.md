![MVP_Logo.pdf](images/MVP_Logo.png){width:150px;height:100px;}

[![Conda](https://img.shields.io/conda/vn/bioconda/mvip.svg?label=Conda&color=green)](https://anaconda.org/bioconda/mvip)
[![PyPI](https://img.shields.io/pypi/v/mvip.svg?label=PyPI&color=green)](https://pypi.python.org/pypi/mvip)
[![Conda downloads](https://img.shields.io/conda/dn/bioconda/mvip.svg?label=Conda%20downloads&color=blue)](https://anaconda.org/bioconda/mvip)

# **MVP v.1.1.2: Modular Viromics Pipeline**

## QUICK LINKS
[Overview](https://gitlab.com/ccoclet/mvp/-/blob/main/README.md#overview)  
[Databases and versions](https://gitlab.com/ccoclet/mvp/-/blob/main/README.md#databases-and-versions)  
[Installation](https://gitlab.com/ccoclet/mvp/-/blob/main/README.md#installation)  
[Quick start](https://gitlab.com/ccoclet/mvp/-/blob/main/README.md#quick-start)  
[Main output files](https://gitlab.com/ccoclet/mvp/-/blob/main/README.md#main-output-files)  
[References](https://gitlab.com/ccoclet/mvp/-/blob/main/README.md#references)  
[Contributing](https://gitlab.com/ccoclet/mvp/-/blob/main/README.md#contributing)  
[License / Copyright](https://gitlab.com/ccoclet/mvp/-/blob/main/README.md#license-copyright)

## OVERVIEW
**MVP** stands for **M**odular **V**iromics **P**ipeline. It is a simplified pipeline that utilizes a suite of state-of-art tools for studying viruses identified from sequencing data (and more):
1. [**geNomad**](https://github.com/apcamargo/genomad): identify viruses, proviruses, and plasmids in sequencing data,
1. [**CheckV**](https://bitbucket.org/berkeleylab/checkv/src/master/): assess the quality, and completeness of identified viral genomes,  
1. **Clustering**: a custom code for a rapid genome clustering based on pairwise ANI (also provided with [**CheckV**](https://bitbucket.org/berkeleylab/checkv/src/master/)),
1. [**Bowtie2**](https://github.com/BenLangmead/bowtie2), [**minimap2**](https://github.com/lh3/minimap2), [**Samtools**](https://github.com/samtools/samtools), and [**CoverM**](https://github.com/wwood/CoverM): calculate coverage of individual viral OTUs by read mapping,
1. **Generating coverage table**: a custom code to create a vOTU table of abundance,
1. **MMseqs2** and **HMMER**: gene prediction & Functional Annotation.

It is a quick and intuitive way to get a list of viral sequences and their properties that can be used for downstream analyses. The main contributors of each software used in MVP should be acknowledged (Citations and links are provided):  

![MVP_Workflow.pdf](images/MVP_Complete_Workflow.png){width:150px;height:100px;}

## INSTALLATION
### Conda installation
```
conda create -n mvip -c conda-forge -c bioconda mvip
conda activate mvip
mvip -h
```

### Installing the latest version of MVP from this repository
- First, open your terminal and clone the MVP repository to get the latest version of the scripts
```bash
git clone https://gitlab.com/ccoclet/mvp.git
```
- Next, create the corresponding conda environment and install the required packages  
```bash
cd mvp
mamba (or conda) env create -f mvp_environment.yaml
```
- To activate this environment, use
```bash
mamba activate mvp
flit publish
```

*Notes:*   
*(1) We recommend to use mamba rather than conda to install MVP for a quicker and more reliable installation process.*  

*(2) If you work on MacOS, you need to use mvp_mac_environment.yaml as CoverM is not available currently for MacOS systems*
```bash
mamba (or conda) env create -f mvp_mac_environment.yaml
mamba activate mvp
```
*(3) If not already done, you might need to install flit.*
```bash
(python3 -m pip install flit)
```

## METADATA AND DIRECTORIES
To start using MVP, you will need input files and directories:  
- a **working directory** (often named based on your project name) where MVP will create the output files,  
- your **sequencing files** (.fna, .fasta, or .fa) in a directory readable by MVP (in the example below, we will use a directory called **00_ASSEMBLY_FILES**),  
- your **read files** (.fastq, .fastq.gz) in a directory reable by MVP, if you want to run Modules 04 and 05 (read mapping and abundance table). In the example below, we will use a directory called **00_READ_FILES**,  
- a **metadata** (.txt) with 4 columns: Sample_number (sample group number), Sample (sample name), Assemply_Path (the absolute path of your input sequencing data files), Read_Path (the absolute path of your read files .fastq or .fastq.gz) (see example below for the content of the metadata).

| Sample_number | Sample         | Assembly_Path                                           | Read_Path                                         | Variable |
| :---:         |     :---:      |        :---:                                            |        :---:                                      | :---:  |
| 1             | sample_name_1  | path/to/00_ASSEMBLY_FILES/sample_name_1_assembly.fna    | path/to/00_READ_FILES/sample_name_1_read.fastq.gz | variable_1 |
| 2             | sample_name_2  | path/to/00_ASSEMBLY_FILES/sample_name_2_assembly.fna    | path/to/00_READ_FILES/sample_name_2_read.fastq.gz | variable_1 |
| 3             | sample_name_3  | path/to/00_ASSEMBLY_FILES/sample_name_3_assembly.fasta  | path/to/00_READ_FILES/sample_name_3_read_R1.fastq.gz | variable_2 |
| 3             | sample_name_4  | path/to/00_ASSEMBLY_FILES/sample_name_4_assembly.fasta  | path/to/00_READ_FILES/sample_name_4_read_R1.fastq.gz | variable_2 |
| 3             | sample_name_5  | path/to/00_ASSEMBLY_FILES/sample_name_5_assembly.fasta  | path/to/00_READ_FILES/sample_name_5_read_R1.fastq.gz | variable_2 |
| 4             | sample_name_6  | path/to/00_ASSEMBLY_FILES/sample_name_6_assembly.fa     | path/to/00_READ_FILES/sample_name_6_read.fastq.gz | variable_2 |
| 5             | sample_name_7  | path/to/00_ASSEMBLY_FILES/sample_name_7_assembly.fa     | path/to/00_READ_FILES/sample_name_7_read.fastq.gz | variable_3 |


*Notes:*  
*(1) If you run MVP for multiple projects and want to keep track of the input/output, we encourage you to save your metadata files and/or your sequencing and read files in directories such as **00_ASSEMBLY_FILES**, and **00_READ_FILES** in the working directory.*  
*(2) If you have forward and reverse reads split into R1 and R2 files, you can just provide the forward R1 read file path in the column **Read_Path** of your metadata. If not already present, be sure to include **```R1```** and **```R2```** in the name of your forward R1 and reverse R2 read files. The script will find the path of the reverse R2 read file by itself if it is identical to the R1 file with just R1 changed to R2.*  

## RUNNING THE PIPELINE - NORMAL MODE
```mvip -h  
```

### Executing Module 00 (MVP Setup)
```mvip MVP_00_set_up_MVP -h  
mvip MVP_00_set_up_MVP -i WORKING_DIRECTORY/ -m data/example_metadata.txt
```
#### Flag explanations
- ```-i``` (required) Path to the working directory where MVP will be run.  
- ```-m``` (required) Path to the metadata that will be use to run MVP.  
- ```--skip_install_databases``` argument to use if you haven't already installed geNomad and CheckV databases, or want to reinstall them (turned off by default).   
- ```--genomad_db_path``` Path to the directory where geNomad database will be installed.   
- ```--checkv_db_path``` Path to the directory where CheckV database will be installed.   
- ```--skip_check_errors``` argument to use if you want to skip to run sequence data error checking (turned off by default).   

#### Module and output explanations
This module will first check for any potential errors/issues in your metadata and your sequencing/read files:  
- missing or extra columns, wrong column names,  
- empty cells,  
- wrong (i.e. unreadable) paths to your sequencing or read files,  
- any potential sequence errors (any characters different than A, C, T, G, or N),  
- duplicate hearders.  

Once your metadata has been checked, the module will create all the directories that MVP needs: **00_DATABASES**, **01_GENOMAD**, **02_CHECK_V**, **03_CLUSTERING**, **04_READ_MAPPING**, **05_VOTU_TABLES** and **06_FUNCTIONAL_ANNOTATION**.  
Finally, if you use the ```--skip_install_databases``` argument, the module won't install the geNomad and checkV databases in **00_DATABASES**, or in the paths provided by ```--genomad_db_path``` and/or ```--checkv_db_path```, respectively. MVP will skip these steps if the databases already exist.

*Notes:*  
*(1) We highly encourage you to make sure that the geNomad and checkV databases are available on your system before deciding if you want to use ```--skip_install_databases``` or not. If you decide to not use the argument while the databases are not installed, you won't have any errors at this step, however the Module 01 won't work.*  


### Executing Module 01 (Running geNomad and CheckV)
```
mvip MVP_01_run_genomad_checkv -h  
mvip MVP_01_run_genomad_checkv -i WORKING_DIRECTORY/ -m data/example_metadata.txt
```
#### Flag explanations
- ```-i``` (required) path to your working directory where all the MVP outputs will be generated and stored.  
- ```-m``` (required) your metadata file.  
- ```--sample_group``` specify one number or a list of numbers in the metadata file you want to process (by default, MVP will process all datasets listed in the metadata file one after the other).  
- ```--skip_modify_headers``` if you want to modify the name of each sequence by prefixing with the sample name (default = false).  
- ```--min_seq_size``` if you want to filter each input file based on a minimum sequence length (in bp, default = 0).  
- ```--genomad_relaxed``` or ```--genomad_conservative``` relaxed and conservative post-classification filters to disable the post-classification filters or to be very conservative with your classification, respectively, preventing sequences without strong support from being classified as plasmid or virus.  
- ```--genomad_db_path``` and ```--checkv_db_path``` these optional arguments are used to provide the paths to geNomad and CheckV, respectively, if they were not installed with the script 00_set_up_mvp.py and are not located into **01_GENOMAD** and **02_CHECK_V**. If you used 00_set_up_mvp.py, then MVP will find the databases by itself and you don't need to specify anything.
- ```--force_genomad``` and ```--force_checkv``` arguments to force geNomad and/or CheckV execution even if the directories already exists (default = do not overwrite existing directories).  
- ```--threads``` set number of threads (default = 1).

#### Module and output explanations
This module will create sample directory, run two rounds of geNomad and CheckV on each sample and return results inside four directories into respective sample directory in **01_GENOMAD** and **02_CHECK_V**:
- **```<sample_name>```_Viruses_Genomad_Output**,  
- **```<sample_name>```_Viruses_CheckV_Output**,  
- **```<sample_name>```_Proviruses_Genomad_Output**,  
- **```<sample_name>```_Proviruses_CheckV_Output**.  

The **```<sample_name>```_virus_summary.tsv**, **proviruses_virus_summary.tsv**, and both **quality_summary.tsv** for viruses and proviruses tabular files summarize the results that were generated by the two rounds of geNomad and CheckV. These 4 files will be used to run Module 02.  

The second round of geNomad and CheckV is used to properly process proviruses trimmed by CheckV by computing a geNomad annotation and score only on the predicted provirus (instead of including the host contamination flagged by CheckV) and predict completeness with CheckV on this trimmed provirus. If none of the contigs was trimmed by the first round of CheckV, proviruses.fna file will be empty and empty files will be created for the second round of geNomad and CheckV.  

Summary reports **```<sample_name>```_MVP_01_Summary_Report.txt** are also generated and stored in the respective ```<sample_name>``` directories in **01_GENOMAD**.

*Notes:*  
*(1) This module will first create a new directory called **00_MODIFIED_ASSEMBLY_FILES** if you used the ```--modify_headers``` or ```--min_seq_size``` arguments, to store the modified assembly files.*  
*(2) We highly encourage not using ```--skip_modify_headers``` if some of your contigs across the different FASTA files may have identical names, if your FASTA files come from various analyses, or if the headers of your sequences do not have a consistent format.*  
*(2) MVP will skip geNomad and/or CheckV steps if the directories already exist and are not empty, unless you use ```--force_genomad``` and ```--force_checkv``` arguments.*  
*(3) You can check the Github repositories of [geNomad](https://github.com/apcamargo/genomad) and [CheckV](https://bitbucket.org/berkeleylab/checkv/src/master/) for more explanation on argument and output files.*  

### Executing Module 02 (Filtering viral prediction)
```
mvip MVP_02_filter_genomad_checkv -h
mvip MVP_02_filter_genomad_checkv -i WORKING_DIRECTORY/ -m data/example_metadata.txt
```
#### Flag explanations
- ```-i``` (required) path to your working directory where all the MVP outputs will be generated and stored.  
- ```-m``` (required) your metadata file.  
- ```--sample_group``` specify one number or a list of numbers in the metadata file you want to process (by default, MVP will process all datasets listed in the metadata file one after the other).  
- ```--viral_min_genes``` minimum number of viral genes required to consider a virus prediction (based on CheckV annotation, default = 1).
- ```--host_viral_genes_ratio``` maximum ratio of host genes to viral genes required to consider a virus prediction (based on CheckV annotation, default = 1, i.e. no more host genes than viral genes).  

#### Module and output explanations
This module will merge and filter **```<sample_name>```_virus_summary.tsv**, **proviruses_virus_summary.tsv**, and both **quality_summary.tsv** for viruses and proviruses tabular files in the respective **```<sample_name>```_Viruses_CheckV_Output**. It will return to a single tabular file for each sample called **```<sample_name>```_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv**. This tabular file lists all the viruses and proviruses that geNomad predicted and that passed the cutoffs, and gives you all geNomad and CheckV features (i.e. virus length, viral genes, completeness, taxonomy, etc.). 

Then the module will create concatenated FASTA files for each sample of the identified virus and trimmed proviruses sequences called **MVP_02_```<sample_name>```_viruses_proviruses_Sequences.fna**.  

Summary reports **```<sample_name>```_MVP_02_Summary_Report.txt** are also generated and stored in the respective ```<sample_name>``` directories in **02_CHECK_V**.  

*Notes:*  
*(1) You can choose to modify the ```--viral_min_genes``` and ```--host_viral_genes_ratio``` arguments at this step to filter your list of identified virus and proviruses sequences based on the number of viral genes. However, we recommend to keep these arguments at their default value in order to keep a comprehensive list of potential virus and proviruses at this step. You will be able to further filter your final tabular file using these arguments when you will run the Module 05.*

### Executing Module 03 (Clustering)
```
mvip MVP_03_do_clustering -h
mvip MVP_03_do_clustering -i WORKING_DIRECTORY/ -m data/example_metadata.txt
```
#### Flag explanations
- ```-i``` (required) path to your working directory where all the MVP outputs will be generated and stored.  
- ```-m``` (required) your metadata file.  
- ```--min_ani``` minimum ANI (Average Nucleotide Identity) value for clustering (default = 95).  
- ```--min_tcov``` minimum coverage (Aligned Fraction, or AF) of the target sequence (default = 85).  
- ```--min_qcov``` minimum coverage (Aligned Fraction, or AF) of the query sequence (default = 0).  
- ```--read_type``` sequencing data type (e.g. short vs long reads) (default = short).  
- ```--Unfiltered_protein_file``` create protein FASTA file from unfiltered virus sequence. Default = False. Warning = If argument provided, the script might run for a long period of time.  
- ```--threads``` set number of threads (default = 1).  

#### Module and output explanations
This module will first merge all the **```<sample_name>```_viruses_proviruses.fna** FASTA files and all **```<sample_name>```_virus_summary.tsv** generated by Module 02. It will return to a single FASTA file **MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences.fna** and 2 tables **MVP_03_All_Sample_Unfiltered_Merged_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv** and **MVP_03_All_Sample_Filtered_Relaxed_Merged_Genomad_CheckV_Virus_Proviruses_Quality_Summary.tsv** in **03_CLUSTERING**. 

Then, the module will use these newly generated FASTA and table files to do a rapid genome clustering based on pairwise ANI, and return to 1 FASTA file and 3 tabular files:  
- **MVP_03_All_Sample_Genomad_CheckV_Virus_Representative_Sequences.fna**: a FASTA file containing all the representative sequences.  
- **MVP_03_All_Sample_Filtered_Relaxed_Merged_Genomad_CheckV_Representative_Virus_Proviruses_Quality_Summary.tsv**: Results of a greedy clustering, using by default the MIUVIG recommended-parameters (95% ANI + 85% AF), along with all geNomad and CheckV information for each sequence/cluster.  
- **MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences_Clustering.tsv**: all-vs-all blastn of sequences.  
- **MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences_Clustering_ANI.tsv**: pairwise ANI between sequence pairs.  
- **MVP_03_All_Sample_Filtered_Relaxed_Virus_Provirus_Sequences_Clustering_ANI_Clusters.tsv**: Results of a greedy clustering, using by default the MIUVIG recommended-parameters (95% ANI + 85% AF).  

The module will generate a **MVP_03_summary_report.txt** file providing an overview of key statistics, quality assessments, and taxonomy distributions.  

The module will build an index using bowtie2-build (short reads) or minimap2 (long reads) from your FASTA file containing the representative sequences in the **04_READ_MAPPING** directory (in preparation of Module 04).  

Finally, the module will create 2 FASTA files containing protein sequences for both representative viruses and all viruses, respectively and geNomad functional annotation tables in **06_FUNCTIONAL_ANNOTATION**.  

*Notes:*  
*(1) **MVP_03_summary_report.txt** will be completed with read mapping information in Module 05.*  
*(2) bowtie2-build outputs a set of 6 files with suffixes ```<reference>.1.bt2```, ```<reference>.2.bt2```, ```<reference>.3.bt2```, ```<reference>.4.bt2```, ```<reference>.rev.1.bt2```, and ```<reference>.rev.2.bt2``` in **04_READ_MAPPING**. These files together constitute the index: they are all that is needed to align reads to that reference in Module 04.*  
*(3) If you work with long read data sequencing (e.g. PacBio, Oxford Nanpore, Illumina Complete Long reads), we recommand to use the argument ```--read-type long```. MVP will then use minimap2 to build the index (reference) needed in Module 04. It will return to a single file called ```reference.mmi``` in **04_READ_MAPPING**.

### Executing Module 04 (Read mapping)
```
mvip MVP_04_do_read_mapping -h
mvip MVP_04_do_read_mapping -i WORKING_DIRECTORY/ -m data/example_metadata.txt --delete_files
```
#### Flag explanations
- ```-i``` (required) path to your working directory where all the MVP outputs will be generated and stored.  
- ```-m``` (required) your metadata file.  
- ```--sample_group``` specify one number or a list of numbers in the metadata file you want to process (by default, MVP will process all datasets listed in the metadata file one after the other).  
- ```--force_read_mapping``` argument to force read mapping execution even if the directory already exists (default = do not overwrite existing directory).  
- ```--read_type``` sequencing data type (e.g. short vs long reads) (default = short).  
- ```--interleaved``` argument use Bowtie2 for interleaved reads (default = TRUE).  
- ```--delete_files``` if you want MVP to delete all intermediary files once a sample is done.  
- ```--threads``` set number of threads (default = 1).  

#### Module and output explanations
This module will generate **```<sample_name>```.sam** by using bowtie2 (short reads) or minimap2 (long reads), and **```<sample_name>```.bam**, and **```<sample_name>```_sorted.bam** files by using bowtie2 to map reads from individual samples to the vOTU database generated in Module 03. Then, the module will use CoverM to calculate coverage based on read mapping, using the sorted BAM files sorted by reference, and return to one tabular file per sample : **```<sample_name>```MVP_04_CoverM.csv** containing the different coverage measures for each viral sequences. Finally, a summary report will be generated: **```<sample_name>```MVP_04_Summary_Report.txt**.  

*Notes:*  
*(1) You can check the Github repositories of [Bowtie2](https://github.com/BenLangmead/bowtie2), [minimap2](https://github.com/lh3/minimap2), [Samtools](https://github.com/samtools/samtools), and [CoverM](https://github.com/wwood/CoverM) for more explanation on argument and output files.*

### Executing Module 05 (Creating vOTU tables)
```
mvip MVP_05_create_vOTU_table -h
mvip MVP_05_create_vOTU_table -i WORKING_DIRECTORY/ -m data/example_metadata.txt
```
#### Flag explanations
- ```-i``` (required) path to your working directory where all the MVP outputs will be generated and stored.  
- ```-m``` (required) your metadata file.  
- ```--covered_fraction``` minimum horizontal coverage fraction required to consider a coverage in the abundance tables. By default, MVP will output abundance tables with minimum covered fraction of 0.1, 0.5, and 0.9.
- ```--normalization``` which CoverM coverage metrics (```RPKM``` or ```FPKM```) you want for your abundance tables (default = RPKM).
- ```--filtration``` inclusion criteria you want to apply on the predicted viruses for your abundance tables. Can be  ```relaxed``` or ```conservative``` (default = conservative). These two levels are pre-defined combinations of minimum completeness, minimum viral genes, minimum length, and/or maximum host viral genes ratio (see below for a detailed explanation of each). Alternatively, custom cutoffs combinations can be applied using individual arguments below.
- ```--viral_min_genes``` minimum number of viral genes required to include a virus prediction (based on CheckV annotation, default = 1).
- ```--host_viral_genes_ratio``` maximum ratio of host genes to viral genes required to include a virus prediction (default = 1).  

#### Module and output explanations
This module will merge all the **```<sample_name>```_CoverM.csv** tabular files to create an unfiltered viral OTU table and save it as **Unfiltered_RPKM_vOTU_table** in **05_VOTU_TABLES**. Then, the module will create a set of viral OTU tables based on the cutoffs (*i.e.*, horizontal coverage) and filtration mode (*i.e.*, conservative and relaxed) you choose. Finally, the module will complete the **MVP_05_summary_report.txt** generated in Module 03 with an overview of normalized abundance measures for vOTUs.

```--filtration``` argument:  
```conservative``` will apply the following cutoffs: only include viral sequences predicted as ≥50% complete by CheckV (AAI prediction) or viral sequences ≥5kb.  
```relaxed``` will include all viral sequences that were gathered and clustered in Module 03.  

*Notes:*  
*(1) We strongly encourage to run the Module 05 with ```--filtration conservative``` to filter your vOTU tables. The conservative mode will only keep Complete, High- and Medium-quality, and ≥5kb Low-quality vOTUs, and is usually a good default for most viral ecogenomics studies.*  
*(2) The last two argument (```--viral-min-genes``` and ```--host-viral-genes-ratio```) can also be used when you run Module 02. They are provided in Module 05 to allow the users to run only one round of clustering (Module 03) and read mapping (Module 04), and then test different cutoffs in Module 05 to evaluate their impacts on the final results.*

### Executing Module 06 (Functional prediction)
```
mvip MVP_06_do_functional_annotation -h
mvip MVP_06_do_functional_annotation -i WORKING_DIRECTORY/ -m data/example_metadata.txt
```
#### Flag explanations
- ```-i``` (required) path to your working directory where all the MVP outputs will be generated and stored.  
- ```-m``` (required) your metadata file.  
- ```--fasta_files``` Sequence and protein FASTA files (representative or all sequences) to use for functional annotation (Default = representative').  
- ```--PHROGS_evalue``` Significance e-value of match between target sequences and query (default = 0.01).  
- ```--PHROGS_score``` Score of match between target sequences and query (default = 60).  
- ```--PFAM_evalue``` Significance e-value of match between target sequences and query (default = 0.01).  
- ```--PFAM_score``` Score of match between target sequences and query (default = 50). 
- ```--ADS``` if you want MVP to searchAnti-Defense Systems.     
- ```--ADS_evalue``` Significance e-value of match between target sequences and query (default = 0.01).  
- ```--ADS_score``` Score of match between target sequences and query (default = 60).  
- ```--ADS_seqid``` Sequence identity of match between target sequences and query (default = 30).  
- ```--RdRP``` if you want MVP to create the 07_RDRP_PHYLOGENY folder and search RdRP profiles.  
- ```--RdRP_evalue``` Significance e-value of match between target sequences and query (default = 0.01). 
- ```--RdRP_score``` Score of match between target sequences and query (default = 50).  
- ```--DRAM``` if you want MVP to create an input file to be process through DRAM-v.  
- ```--force_prodigal``` force execution of protein prediction by Prodigal.
- ```--force_PHROGS``` force PHROGS annotation.
- ```--force_PFAM``` force PFAM annotation.
- ```--force_ADS``` force ADS annotation.
- ```--force_RdRP``` force RdRP annotation.
- ```--force_outputs``` force creation of final annotation table even though it exists.
- ```--delete_files``` if you want MVP to delete all intermediary files once the functional annotation is done.  
- ```--threads``` set number of threads (default = 1).  

#### Module and output explanations
This module will use one of the FASTA files (i.e. unfiltered, filtered relaxed contigs, or filtered relaxed vOTUs) containing protein sequences generated by the Module 03 to search protein sequences against multiple databases (i.e. PHROGS, PFAM, Anti-defense systems, and/or RdRP) and return to unfiltered annotation tables in **06_FUNCTIONAL_ANNOTATION**, for each annotation. Then, the module will filter all of these tables using score, e-value, and sequence identity thresholds and merge all tables in a a single one will all functional annotation: **MVP_06_All_Sample_Filtered_Relaxed_Merged_Genomad_CheckV_Representative_Virus_Proviruses_Gene_Annotation_GENOMAD_PHROGS_PFAM_ADS_RDRP_Filtered.tsv**.  

If you use argument ```--RDRP```, the module will create a new folder **06_RDRP_ANNOTATION**, search the protein sequences against RdRP HMM profiles, and return to  ```06C_Filtered_Formatted_RdRP_Profile_Tab.tsv``` that can be used for downstream RdRP phylogeny analyses, for example.  

If you use ```--DRAM```, the module will create a new folder **06_DRAM_V**, and generate an input table **MVP_06_All_Sample_Filtered_Relaxed_Merged_Genomad_CheckV_Representative_Virus_Proviruses_Gene_Annotation_GENOMAD_DRAM_Input.tsv** that can be used to run DRAM-v.  

Finally, the module will create a **MVP_06_summary_report.txt** generated with an overview of the functional annotation.  

*Notes:*  
*(1) We  encourage to run the Module 06 with ```--fasta_files representative``` (by default).*  

### Executing Module 07 (Binning viral genomes)
```
mvip MVP_07_do_binning -h
mvip MVP_07_do_binning -i WORKING_DIRECTORY/ -m data/example_metadata.txt
```
#### Flag explanations
- ```-i``` (required) path to your working directory where all the MVP outputs will be generated and stored.  
- ```-m``` (required) your metadata file.  
- ```--binning_sample_group``` specify one number or a list of numbers in the metadata file you want to process by vRhyme for binning (by default, MVP will process all datasets listed in the metadata file one after the other).  
- ```--read_mapping_sample_group``` specify one number or a list of numbers in the metadata file you want to process for the read mapping step of the vBins (by default, MVP will process all datasets listed in the metadata file one after the other).  
- ```--keep_bam``` If used, do not remove sorted BAM files generated by vRhyme. Otherwise all unsorted/index BAM files generated from vRhyme read alignment or SAM conversions will be deleted (default = TRUE).  
- ```--force_vrhyme``` argument force vRhyme execution even if the directory 07A_vRHYME_OUTPUT already exists (default = do not overwrite existing directory).  
- ```--force_checkv``` argument force CheckV execution even if the directory 07B_vBINS_CHECKV already exists (default = do not overwrite existing directory).  
- ```--force_read_mapping``` argument force read mapping step even if the directory 07C_vBINS_READ_MAPPING already exists (default = do not overwrite existing directory).  
- ```--read_type``` sequencing data type (e.g. short vs long reads) (default = short).  
- ```--interleaved``` argument use Bowtie2 for interleaved reads (default = TRUE).  
- ```--delete_files``` if you want MVP to delete all intermediary files once a sample is done.  
- ```--force_outputs``` argument force the creation of ouptut tables even if the tables already exist (default = do not overwrite existing files).
- ```--filtration``` relaxed or conservative vRhyme post-filtration to remove potential contaminated vBins (default = conservative).  
- ```--threads``` set number of threads (default = 1).  

#### Module and output explanations
This module will use the FASTA file containing viral sequences generated by the Module 03 to run vRhyme for binning virus genomes and return  outputs in  . 
The module will generate a folder **vRhyme_best_bins_fasta** containing fasta files for best vbins and ```Merged_vRhyme_Outputs_Unfiltered_best_vBins_Memberships_geNomad_CheckV_Summary_Table.tsv``` that summarize vRhyme output tables in **07A_vRHYME_OUTPUT**.  
Then, the module will run CheckV and do the read mapping on vBin sequences and return results in **07B_vBINS_CHECKV** and **07C_vBINS_READ_MAPPING**, respectively. This will generate two output files: ```Unfiltered_best_vBins_read_mapping_information_Table.tsv``` and ```Merged_vRhyme_Outputs_Unfiltered_best_vBins_Memberships_geNomad_CheckV_Summary_read_mapping_information_Table.tsv```.  
The module will then generate three filtered coverage tables based on the same pattern than the Module 05 (*i.e.*, horizontal coverage) in **07D_vBINS_vOTUS_TABLES**.  
Finally, the module will generate two fasta files in **07E_FASTA_IPHOP_INPUTS**: ```Filtered_filtration_Prokaryote_Unknown_best_vBins_Representative_Unbinned_vOTUs_Sequences_iPHoP_Input.fasta.tsv``` and ```Filtered_Prokaryote_Only_best_vBins_Representative_Unbinned_vOTUs_Sequences_iPHoP_Input.fasta``` that combined vBin and unbinned sequences that are predicted to be phages and unknown or only phages, respectively.  
Finally, the module will create a **MVP_07_Summary_Report.txt** generated with an overview of the functional annotation.  

*Notes:*  
*(1) The coverage tables will combine filtered vBins and unbinned contigs.*  
*(2) All filtration thresholds (checkV and horizontal coverage) are based on previous modules in order to get consistent outputs.*  

### Executing Module 99 (Prepare NCBI MIUViG submission)
```
mvip MVP_99_prep_MIUViG_submission -h
mvip MVP_99_prep_MIUViG_submission -i WORKING_DIRECTORY/ -m data/example_metadata.txt
```
#### Flag explanations
- ```-i``` (required) path to your working directory where all the MVP outputs will be generated and stored.  
- ```-m``` (required) your metadata file.  
- ```-g``` Identifier of the sequence to be processed.    
- ```-s``` Should be one of "setup_metadata" (to be run first) or "prep_submission" (once sequence metadata have been checked and completed).  
- ```-t``` path to the BioSample submission template file, generated from https://submit.ncbi.nlm.nih.gov/genbank/template/submission/, only required for the step 2: prep_submission  

#### Module and output explanations

### Executing Module 100 (Summarize outputs)
```
mvip MVP_100_summarize_outputs -h
mvip MVP_100_summarize_outputs -i WORKING_DIRECTORY/ -m data/example_metadata.txt
```
#### Flag explanations
- ```-i``` (required) path to your working directory where all the MVP outputs will be generated and stored.  
- ```-m``` (required) your metadata file.  
- ```--force``` force creation of summary reports and figures even though they exist.

#### Module and output explanations
This module will first find the highest module used by the user, calculate the total MVP running time, and create a final summary report containing all the MVP commands used. Then, the module will find and store the main output tables in **100_SUMMARIZED_OUTPUTS**. Finally, the module will execute the corresponding R code based on the highest MVP module ran  by the user. This script essentially automates the process of summarizing outputs from the MVP, including generating report, copying final output files, and integrating R-based data analysis and visualization.

*Notes:*  
*(1) This module creates a folder within **100_SUMMARIZED_OUTPUTS** named with the current date and time. This setup enables users to run the same modules with different arguments or options, or to add new modules. They can then execute Module 100, and this won't delete previous summary folders.*  

## LINK TO GITHUB AND PEER-REVEW PAPERS
Link to [**geNomad github**](https://github.com/apcamargo/genomad)  
[**Camargo, A.P.**, Roux, S., Schulz, F., Babinski, M., Xu, Y., Hu, B., Chain, P. S. G., Nayfach, S., & Kyrpides, N. C. **You can move, but you can’t hide: identification of mobile genetic elements with geNomad.** bioRxiv (2023), DOI: 10.1101/2020.11.01.361691](https://www.biorxiv.org/content/10.1101/2023.03.05.531206v1)  

Link to [**CheckV github**](https://bitbucket.org/berkeleylab/checkv/src/master/)  
[**Nayfach, S.**, Camargo, A.P, Schulz, F. et al. **CheckV assesses the quality and completeness of metagenome-assembled viral genomes.** Nat Biotechnol 39, 578–585 (2021). https://doi.org/10.1038/s41587-020-00774-7](https://www.nature.com/articles/s41587-020-00774-7)  

Link to [**Bowtie2 github**](https://github.com/BenLangmead/bowtie2)  
[**Langmead B**, Salzberg S. **Fast gapped-read alignment with Bowtie 2.** Nature Methods. 2012, 9:357-359](https://www.nature.com/articles/nmeth.1923)  

Link to [**minimap2**](https://github.com/lh3/minimap2)  
[**Li H., New strategies to improve minimap2 alignment accuracy. Bioinformatics.** 2021, 37(23):4572–4574.](https://academic.oup.com/bioinformatics/article/37/23/4572/6384570?login=true)  

Link to [**Samtools github**](https://github.com/samtools/samtools)  
[**Li, H.**, B. Handsaker, A. Wysoker, T. Fennell, J. Ruan, N. Homer, G. Marth, G. Abecasis, R. Durbin, and 1000 Genome Project Data Processing Subgroup. **The Sequence Alignment/Map Format and SAMtools.** Bioinformatics 25, no. 16 2009: 2078–79.](https://academic.oup.com/bioinformatics/article/25/16/2078/204688?login=true)  

Link to [**CoverM github**](https://github.com/wwood/CoverM)  

Link to [**MMseqs2 github**](https://github.com/soedinglab/MMseqs2)  
[**Mirdita M**, Steinegger M, Breitwieser F, Soding J, Levy Karin E. **Fast and sensitive taxonomic assignment to metagenomic contigs.** Bioinformatics, doi: 10.1093/bioinformatics/btab184 (2021).](https://academic.oup.com/bioinformatics/article/37/18/3029/6178277)  

Link to [**HMMER github**](https://github.com/EddyRivasLab/hmmer)  
[**Finn, R.D.**, Clements, J., & Eddy, S. R.  **HMMER web server: interactive sequence similarity searching.** Nucleic acids research, 39(suppl_2), W29-W37 (2011).](https://doi.org/10.1093/nar/gkr367)  

## COPYRIGHT NOTICE
Modular Viromics Pipeline (MVP) Copyright (c) 2023, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.  

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at IPO@lbl.gov.  

NOTICE. This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights.  As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit others to do so.  

## LICENCE AGREEMENT
GPL v3 License  

Modular Viromics Pipeline (MVP) Copyright (c) 2023, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.  

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.  

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
