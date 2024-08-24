import argparse
import os
import datetime
import re
import shutil
import pandas as pd
import subprocess
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import mvip

def fetch_arguments(parser):
    parser.set_defaults(func=main)
    parser.set_defaults(program="MVP_100_summarize_outputs")
    parser.add_argument(
        "--input", "-i",
        help="Path to your working directory where you want to run MVP.",
    )
    parser.add_argument(
        "--metadata", "-m",
        help="Path to your metadata that you want to use to run MVP.",
    )
    parser.add_argument('--force', 
    action='store_true', 
    help='Force execution of all steps, even if final_annotation_output_file exists.',
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

def find_max_module(args):
    max_module = 0
    max_module_folder = ""
    target_directories = ['01_GENOMAD', '02_CHECK_V', '03_CLUSTERING', '04_READ_MAPPING', '05_VOTU_TABLES', '06_FUNCTIONAL_ANNOTATION', '07_BINNING']

    for root, dirs, files in os.walk(args['input']):
        for d in dirs:
            if d in target_directories:
                module_number = int(d.split("_")[0])
                if module_number > max_module and module_number < 99:
                    max_module = module_number
                    max_module_folder = d

    return max_module, max_module_folder

def find_summary_reports(args, max_module_folder):
    target_directories = [os.path.join(args['input']), '01_GENOMAD', '02_CHECK_V', '03_CLUSTERING', '04_READ_MAPPING', '05_VOTU_TABLES', '06_FUNCTIONAL_ANNOTATION', '07_BINNING']
    summary_reports_dict = {}
    
    # Include the base directory in the search for summary reports
    all_directories = [args['input']] + [os.path.join(args['input'], directory) for directory in target_directories]
    
    for directory_path in all_directories:
        summary_reports = []
        if os.path.exists(directory_path):
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if file.endswith("_Summary_Report.txt"):
                        summary_reports.append(os.path.join(root, file))
                if os.path.basename(directory_path) == max_module_folder:  # Check if it's the max_module_folder
                    break  # Stop searching further
            summary_reports_dict[os.path.basename(directory_path)] = summary_reports

    num_summary_reports = len(summary_reports_dict['01_GENOMAD'])

    return summary_reports_dict, num_summary_reports

def create_output_folder(args):
    print(f"\n\033[1m{step_counter.print_main_step()}: Creating the output directory with today's date to store the summary files...\033[0m")

    start_time = datetime.datetime.now()
    formatted_start_time = start_time.strftime("%Y-%m-%d-%Hh%Mmin%Ssec")

    output_folder = os.path.join(args['input'], "100_SUMMARIZED_OUTPUTS", formatted_start_time)
    
    # Check if --force argument is provided
    if args['force']:
        # Delete existing output_folder if it exists
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
    
    # Create the output directory
    os.makedirs(output_folder, exist_ok=True)
    output_filename = os.path.join(output_folder, f"{formatted_start_time}_MVP_100_Summary_Report.txt")
    
    return output_folder, output_filename

def extract_module_info(report_list):
    module_info_list = []
    for report in report_list:
        with open(report, 'r') as file:
            module_info = []
            lines_after_running_time = False
            for line in file:
                if line.startswith('*') or '.py' in line:
                    module_info.append(line.strip())
                # Check if the report is in the specified list
                if os.path.basename(report) in ['MVP_03_Summary_Report.txt', 'MVP_05_Summary_Report.txt', 'MVP_06_Summary_Report.txt', 'MVP_07_Summary_Report.txt']:
                    if lines_after_running_time:
                        module_info.append(line.strip())
                    elif line.startswith('Running Time:'):
                        lines_after_running_time = True
        module_info_list.append("\n".join(module_info))
    return module_info_list

def extract_running_times(report_list, trigger_line):
    running_times = []
    for report in report_list:
        with open(report, 'r') as file:
            found_trigger_line = False
            for line in file:
                if found_trigger_line and line.startswith('Running Time'):
                    match = re.search(r'(\d+.\d+) seconds', line)
                    if match:
                        running_time_str = match.group(1)
                        running_time = float(running_time_str)
                        running_times.append(running_time)
                elif line.startswith(trigger_line):
                    found_trigger_line = True
    return running_times

def calculate_MVP_total_running_time(summary_reports_dict):
    total_running_time = 0
    for directory, data in summary_reports_dict.items():
        total_running_time += sum(extract_running_times(data, directory.split('_')[0]))
    return total_running_time

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

def generate_summary_report(output_filename, max_module, max_module_folder, num_summary_reports, summary_reports_dict):
    print(f"\n\033[1m{step_counter.print_main_step()}: Creating the final summary report...\033[0m")

    with open(output_filename, "w") as f:
        f.write("****************************************************************************\n")
        f.write("************            MVP Module 100 Summary Report            ***********\n")
        f.write("****************************************************************************\n")
        f.write(f"Number of samples processed by MVP: {num_summary_reports}\n")
        f.write(f"Number of MVP modules ran: 0{max_module} ({max_module_folder})\n")
        total_running_time = calculate_MVP_total_running_time(summary_reports_dict)
        f.write(f"Total MVP running time (hours:minutes:seconds): {format_time(total_running_time)}")
        
        # Print running times and means
        for directory, data in summary_reports_dict.items():
            total_seconds = sum(extract_running_times(data, directory.split('_')[0]))
            total_reports = len(data)
            if total_reports > 0:
                module_info = extract_module_info(data)
                f.write("\n")
                f.write(f"\n{module_info[0]}")  # Write only the first 4 lines
                f.write("\n")
                f.write(f"\nTotal running time (hours:minutes:seconds): {format_time(total_seconds)}")
                if total_reports > 1:
                    mean_seconds = total_seconds / total_reports
                    mean_hours = mean_seconds // 3600
                    mean_minutes = (mean_seconds % 3600) // 60
                    mean_seconds %= 60
                    f.write(f"\nMean running time per summary report: {format_time(mean_hours * 3600 + mean_minutes * 60 + mean_seconds)}")

def copy_additional_files(args, max_module_folder, output_folder):
    print(f"\n\033[1m{step_counter.print_main_step()}: Copying main output files in {output_folder}...\033[0m")

    source_files = [
        "MVP_03_All_Sample_Filtered_Relaxed_Merged_Genomad_CheckV_Representative_Virus_Proviruses_Quality_Summary.tsv",
        "MVP_05_All_Sample_Filtered_conservative_Representative_Virus_Proviruses_vOTU_RPKM_Table.tsv",
        "_Filtered.tsv",
        "MVP_07_Merged_vRhyme_Outputs_Filtered_conservative_best_vBins_Representative_Unbinned_vOTUs_geNomad_CheckV_Summary_read_mapping_information_RPKM_Table.tsv"
    ]

    if max_module_folder == '03_CLUSTERING':
        source_files_to_copy = [source_files[0]]
    elif max_module_folder == '05_VOTU_TABLES':
        source_files_to_copy = source_files[:2]
    elif max_module_folder == '06_FUNCTIONAL_ANNOTATION':
        source_files_to_copy = source_files[:3]
    elif max_module_folder == '07_BINNING':
        source_files_to_copy = source_files

    # Get all files containing "_Filtered.tsv" in their names
    additional_files = []
    for root, _, files in os.walk(args['input']):
        for file in files:
            if "_Filtered.tsv" in file:
                additional_files.append(file)

    # Combine the initial set of files and additional files
    source_files += additional_files

    for file in source_files:
        destination_path = os.path.join(output_folder, file)
        # Only copy the file if it doesn't already exist in the output folder
        if not os.path.exists(destination_path):
            # Search for the file in base_directory and its subfolders
            for root, _, files in os.walk(args['input']):
                if file in files:
                    source_path = os.path.join(root, file)
                    shutil.copy(source_path, output_folder)
                    # Convert to CSV if the file is "_Filtered.tsv"
                    if "_Filtered.tsv" in file:
                      with open(destination_path, 'r') as f:
                          data = f.read()
                      with open(destination_path, 'w') as f:
                          f.write(data.replace(',', ';'))                        

                      csv_file = os.path.splitext(destination_path)[0] + ".csv"
                      os.rename(destination_path, csv_file)
                      # Convert to CSV format with comma as separator
                      with open(csv_file, 'r') as f:
                          data = f.read()
                      with open(csv_file, 'w') as f:
                          f.write(data.replace('\t', ','))  # Replace tabs with commas
                    break  # Stop searching if the file is found

def install_r_packages():
    print(f"\n\033[1m{step_counter.print_main_step()}: Installing R packages if not already installed...\033[0m")

    packages_to_install = ["ggplot2", "dplyr", "cowplot", "readr", "complexupset", "stringr", "reshape2", "vegan"]

    installed_packages = subprocess.run('conda list', shell=True, capture_output=True, text=True).stdout

    for package in packages_to_install:
        if f'r-{package}' not in installed_packages:
            print(f"Installing {package}...")
            subprocess.run(f"conda install -c r r-{package} -y", shell=True)

def find_R_tables(output_folder):
    files = os.listdir(output_folder)
    votu_table_file_name = None
    for file in files:
        if file.startswith('MVP_07_'):
            votu_table_file_name = file
            break  # Stop iteration if MVP_07 is found

    if not votu_table_file_name:  # If MVP_07_ file not found
        for file in files:
            if file.startswith('MVP_05_'):
                votu_table_file_name = file
                break
            elif file.startswith('MVP_03_'):
                votu_table_file_name = file
            
    functional_annotation_table_file_path = None
    for file in files:
        if file.startswith('MVP_06_All_Sample_Filtered_Conservative_'):
            functional_annotation_file_name = os.path.join(file)
            break
        elif file.startswith('MVP_06_All_Sample_Filtered_Relaxed_'):
            functional_annotation_file_name = os.path.join(file)

    votu_table_file_path = os.path.join(output_folder, votu_table_file_name)
    functional_annotation_table_file_path = os.path.join(output_folder, functional_annotation_file_name)

    return votu_table_file_name, votu_table_file_path, functional_annotation_table_file_path

def create_module_03_figures(votu_table_file_path, metadata_file_path, output_folder):
    print(f"\n\033[1m{step_counter.print_main_step()}: Generating figures for Module 03 using R...\033[0m")

    r_code = """
library(ggplot2)
library(dplyr)
library(cowplot)
library(readr)
library(ComplexUpset)
library(stringr)
library(reshape2)
library(vegan)

data = read.table("{votu_table_file_path}", h=T, sep="\t", dec=".")

checkv_data <- data %>%
  count(checkv_quality = checkv_quality) %>%
  mutate(checkv_quality = factor(checkv_quality, levels = c("Complete", "High-quality", "Medium-quality", "Low-quality", "Not-determined"))) %>%
  mutate(Factor = "checkv_quality")

# Create the box plot
p_conservative_filtered_vOTUs_CheckV <- ggplot(checkv_data, aes(x = Factor, y = n, fill = checkv_quality)) +
  geom_bar(stat="identity", color = "black", size = 1, width = 0.8) + 
  theme_minimal() +
  scale_fill_manual(values = c("white", "#D3D3D3", "#9D9D9D", "#686868", "#333333"), 
                    limits = c("Not-determined", "Low-quality", "Medium-quality", "High-quality", "Complete"),
                    name="CheckV quality") +
  coord_flip() +
  labs(y = "Number", x = "") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

length_data <- data %>%
  mutate(Length_Category = case_when(
    virus_length < 10000 ~ "<10 kb",
    virus_length >= 10000 & virus_length <= 50000 ~ "10-50 kb",
    TRUE ~ ">50 kb")) %>%
  count(Length_Category) %>%
  mutate(Length_Category = factor(Length_Category, levels = c("<10 kb", "10-50 kb", ">50 kb"))) %>%
  mutate(Factor = "Length")

p_conservative_filtered_vOTUs_length <- ggplot(length_data, aes(x = Length_Category, y = n)) +
  geom_bar(stat="identity", position= position_dodge(preserve = "single"), fill = '#D3D3D3', color = "black", size = 1) + 
  theme_minimal() +
  coord_flip() +
  labs(y = "Number", x = "Genome length") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

data <- data %>%
  mutate(Taxonomy = sapply(strsplit(as.character(taxonomy), ";"), function(x) {{
    level_5 <- ifelse(length(x) >= 5, x[5], tail(x, 1))
    if (level_5 == "Viruses") {{
      return("Unclassified")
    }} else {{
      return(level_5)
    }}
  }}))

taxa_count_data <- data %>%
  count(Taxonomy = data$Taxonomy) %>%
  mutate(Factor = "Taxonomy")
head(taxa_count_data)

# Define the color palette based on the presence of "Unclassified"
if ("Unclassified" %in% taxa_count_data$Taxonomy) {{
  # If "Unclassified" exists, use one less color than the number of unique taxa
  color_palette <- colorRampPalette(c("#3B9AB1", "#78B7C5", "#EBCC2A", "#E1AE01", "#F22300"))(length(unique(taxa_count_data$Taxonomy)) - 1)
  # Assign #D3D3D3 to Unclassified
  color_palette <- c(color_palette, "#D3D3D3")
}} else {{
  # If "Unclassified" doesn't exist, use the number of unique taxa as the number of colors
  color_palette <- colorRampPalette(c("#3B9AB1", "#78B7C5", "#EBCC2A", "#E1AE01", "#F22300"))(length(unique(taxa_count_data$Taxonomy)))
}}  

# Create the ggplot
p_taxa_vOTUs_counts <- ggplot(taxa_count_data, aes(x = Factor, y = n, fill = Taxonomy)) +
  geom_bar(position = "fill", stat = "identity", color = "black", size = 1) + 
  scale_fill_manual(values = color_palette) +
  labs(x = "", y = "Percentage (%)", fill = "Taxonomy") + 
  theme_minimal() +
  coord_flip() +
  scale_y_continuous(labels = scales::percent_format()) +
  theme(legend.justification = c(0, 0.5), 
        axis.text = element_text(color = "black", size = 14),
        axis.title = element_text(color = "black", size = 14),
        axis.ticks = element_line(size = 0.8, color = "black"),
        axis.ticks.length = unit(0.2, "cm"))

spacer <-  ggplot() +
                geom_blank(fill = "white") +  # Set the background color to white
                theme_void()

title <- ggdraw() + draw_label("Summarized plots generated by MVP\nModule 03 (Clustering)", fontface='bold')

combined_plots <- plot_grid(title, p_conservative_filtered_vOTUs_CheckV, p_conservative_filtered_vOTUs_length, p_taxa_vOTUs_counts,
                                ncol = 1, align = "hv", rel_heights = c(0.3, 0.4, 0.6, 0.6), labels=c('','A','B', 'C'))

ggsave("{output_folder}/Summarize_output_plots.pdf", plot = combined_plots, width = 8, height = 8)
    """.format(votu_table_file_path=votu_table_file_path, metadata_file_path=metadata_file_path, output_folder=output_folder)

    # Run the R code
    robjects.r(r_code)

def create_module_03_06_figures(votu_table_file_path, metadata_file_path, functional_annotation_table_file_path, output_folder):
    print(f"\n\033[1m{step_counter.print_main_step()}: Generating figures for Module 03 and Module 06 using R...\033[0m")


    r_code = """
library(ggplot2)
library(dplyr)
library(cowplot)
library(readr)
library(ComplexUpset)
library(stringr)
library(reshape2)
library(vegan)

data = read.table("{votu_table_file_path}", h=T, sep="\t", dec=".")

checkv_data <- data %>%
  count(checkv_quality = checkv_quality) %>%
  mutate(checkv_quality = factor(checkv_quality, levels = c("Complete", "High-quality", "Medium-quality", "Low-quality", "Not-determined"))) %>%
  mutate(Factor = "checkv_quality")

# Create the box plot
p_conservative_filtered_vOTUs_CheckV <- ggplot(checkv_data, aes(x = Factor, y = n, fill = checkv_quality)) +
  geom_bar(stat="identity", color = "black", size = 1, width = 0.8) + 
  theme_minimal() +
  scale_fill_manual(values = c("white", "#D3D3D3", "#9D9D9D", "#686868", "#333333"), 
                    limits = c("Not-determined", "Low-quality", "Medium-quality", "High-quality", "Complete"),
                    name="CheckV quality") +
  coord_flip() +
  labs(y = "Number", x = "") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

length_data <- data %>%
  mutate(Length_Category = case_when(
    virus_length < 10000 ~ "<10 kb",
    virus_length >= 10000 & virus_length <= 50000 ~ "10-50 kb",
    TRUE ~ ">50 kb")) %>%
  count(Length_Category) %>%
  mutate(Length_Category = factor(Length_Category, levels = c("<10 kb", "10-50 kb", ">50 kb"))) %>%
  mutate(Factor = "Length")

p_conservative_filtered_vOTUs_length <- ggplot(length_data, aes(x = Length_Category, y = n)) +
  geom_bar(stat="identity", position= position_dodge(preserve = "single"), fill = '#D3D3D3', color = "black", size = 1) + 
  theme_minimal() +
  coord_flip() +
  labs(y = "Number", x = "Genome length") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

data <- data %>%
  mutate(Taxonomy = sapply(strsplit(as.character(taxonomy), ";"), function(x) {{
    level_5 <- ifelse(length(x) >= 5, x[5], tail(x, 1))
    if (level_5 == "Viruses") {{
      return("Unclassified")
    }} else {{
      return(level_5)
    }}
  }}))

taxa_count_data <- data %>%
  count(Taxonomy = data$Taxonomy) %>%
  mutate(Factor = "Taxonomy")
head(taxa_count_data)

# Define the color palette based on the presence of "Unclassified"
if ("Unclassified" %in% taxa_count_data$Taxonomy) {{
  # If "Unclassified" exists, use one less color than the number of unique taxa
  color_palette <- colorRampPalette(c("#3B9AB1", "#78B7C5", "#EBCC2A", "#E1AE01", "#F22300"))(length(unique(taxa_count_data$Taxonomy)) - 1)
  # Assign #D3D3D3 to Unclassified
  color_palette <- c(color_palette, "#D3D3D3")
}} else {{
  # If "Unclassified" doesn't exist, use the number of unique taxa as the number of colors
  color_palette <- colorRampPalette(c("#3B9AB1", "#78B7C5", "#EBCC2A", "#E1AE01", "#F22300"))(length(unique(taxa_count_data$Taxonomy)))
}}  

# Create the ggplot
p_taxa_vOTUs_counts <- ggplot(taxa_count_data, aes(x = Factor, y = n, fill = Taxonomy)) +
  geom_bar(position = "fill", stat = "identity", color = "black", size = 1) + 
  scale_fill_manual(values = color_palette) +
  labs(x = "", y = "Percentage (%)", fill = "Taxonomy") + 
  theme_minimal() +
  coord_flip() +
  scale_y_continuous(labels = scales::percent_format()) +
  theme(legend.justification = c(0, 0.5), 
        axis.text = element_text(color = "black", size = 14),
        axis.title = element_text(color = "black", size = 14),
        axis.ticks = element_line(size = 0.8, color = "black"),
        axis.ticks.length = unit(0.2, "cm"))

if ("_ADS_" %in% str_extract("{functional_annotation_table_file_path}", "_ADS_")) {{
    data_M06 <- readr::read_csv("{functional_annotation_table_file_path}", col_types = cols(ADS_Defense_type = col_character()))
    data_M06$PHROGS_Category <- ifelse(is.na(data_M06$PHROGS_Category), "unknown", data_M06$PHROGS_Category)
    data_M06$PFAM_Annotation <- ifelse(is.na(data_M06$PFAM_Annotation), "unknown", data_M06$PFAM_Annotation)
    data_M06$ADS_Defense_type <- ifelse(is.na(data_M06$ADS_Defense_type), "unknown", data_M06$ADS_Defense_type)
    # Initialize lists for each annotation method
    ADS_list <- data.frame(Viral_gene_ID = character(0))
    Pfam_list <- data.frame(Viral_gene_ID = character(0))
    PHROGS_list <- data.frame(Viral_gene_ID = character(0))
    geNomad_list <- data.frame(Viral_gene_ID = character(0))

    # Filter data for each annotation method and populate the lists
    ADS_list <- data_M06 %>%
    filter(ADS_Defense_type != "unknown" & ADS_Defense_type != "Unknown") %>%
    select(Viral_gene_ID)

    # Filter out rows based on PFAM_Annotation column
    Pfam_list <- data_M06 %>%
    filter(!grepl(paste(c("unknown", "Unknown", "Uncharacterized"), collapse = "|"), PFAM_Annotation)) %>%
    select(Viral_gene_ID)

    PHROGS_list <- data_M06 %>%
    filter(PHROGS_Category != "unknown" & PHROGS_Category != "Unknown") %>%
    select(Viral_gene_ID)

    geNomad_list <- data_M06 %>%
    filter(GENOMAD_Annotation != "unknown" & GENOMAD_Annotation != "Unknown") %>%
    select(Viral_gene_ID)

    # Combine all lists into a single data frame
    upset_data <- data.frame(Viral_gene_ID = data_M06$Viral_gene_ID,
                            ADS = as.integer(data_M06$Viral_gene_ID %in% ADS_list$Viral_gene_ID),
                            Pfam = as.integer(data_M06$Viral_gene_ID %in% Pfam_list$Viral_gene_ID),
                            PHROGS = as.integer(data_M06$Viral_gene_ID %in% PHROGS_list$Viral_gene_ID),
                            geNomad = as.integer(data_M06$Viral_gene_ID %in% geNomad_list$Viral_gene_ID))

    p_annotation_upset <- upset(
                            upset_data, 
                            name='Group',
                            width_ratio=0.3,
                            c('ADS', 'Pfam', 'PHROGS', 'geNomad'),
                            queries = list(upset_query(set = 'ADS', fill = '#EFE32A'),
                                            upset_query(set = 'Pfam', fill = '#CB1800'),
                                            upset_query(set = 'PHROGS', fill = '#00A87E'),
                                            upset_query(set = 'geNomad', fill = '#61BCEC')),
                            base_annotations=list('Shared genes between groups'=(intersection_size(counts=T, col = "black", 
                                                                                                    bar_number_threshold=1, width=0.8) +
                                                                                    scale_y_continuous(expand=expansion(mult=c(0, 0.05))) + 
                                                                                    theme(panel.grid=element_blank(),
                                                                                        panel.background = element_rect(fill = 'white'),
                                                                                        axis.text.x=element_blank(),
                                                                                        axis.text.y = element_text(color="black", size=14),
                                                                                        axis.title = element_text(color="black", size=14),
                                                                                        axis.title.x=element_blank(),
                                                                                        axis.line=element_line(colour='black')))),
                            set_sizes=(upset_set_size(geom=geom_bar(width=0.6, col = "black"),
                                                        position = 'right') + 
                                        geom_text(aes(label=after_stat(count)), hjust=-0.1, stat='count') +
                                        ylab("Nb of genes per group") +
                                        expand_limits(y=7000) +
                                        theme(panel.background =element_blank(),
                                                axis.line.x=element_line(colour='black'),
                                                axis.ticks.y=element_blank(),
                                                axis.text.y=element_blank(),
                                                axis.text.x = element_text(color="black", size=14),
                                                axis.title.x = element_text(color="black", size=14),
                                                axis.title.y=element_blank())),
                            theme = list(legend.text.align = NULL),
                            matrix=(intersection_matrix(geom=geom_point(shape='circle filled', size=3.5, stroke=0.45)) + 
                                        ylab("Database") +
                                        theme(panel.background =element_blank(),
                                            axis.line=element_blank(),
                                            axis.ticks=element_blank(),
                                            axis.title=element_text(color="black", size=14),
                                            axis.text.y = element_text(color="black", size=14),
                                            axis.text.x=element_blank())),
                            stripes=upset_stripes(geom=geom_segment(linewidth=12), colors=c('grey95', 'white')),
                            sort_sets='descending',
                            sort_intersections='descending')
}} else {{
    data_M06 <- readr::read_csv("{functional_annotation_table_file_path}")
    data_M06$PHROGS_Category <- ifelse(is.na(data_M06$PHROGS_Category), "unknown", data_M06$PHROGS_Category)
    data_M06$PFAM_Annotation <- ifelse(is.na(data_M06$PFAM_Annotation), "unknown", data_M06$PFAM_Annotation)
    # Initialize lists for each annotation method
    Pfam_list <- data.frame(Viral_gene_ID = character(0))
    PHROGS_list <- data.frame(Viral_gene_ID = character(0))
    geNomad_list <- data.frame(Viral_gene_ID = character(0))

    # Filter out rows based on PFAM_Annotation column
    Pfam_list <- data_M06 %>%
    filter(!grepl(paste(c("unknown", "Unknown", "Uncharacterized"), collapse = "|"), PFAM_Annotation)) %>%
    select(Viral_gene_ID)

    PHROGS_list <- data_M06 %>%
    filter(PHROGS_Category != "unknown" & PHROGS_Category != "Unknown") %>%
    select(Viral_gene_ID)

    geNomad_list <- data_M06 %>%
    filter(GENOMAD_Annotation != "unknown" & GENOMAD_Annotation != "Unknown") %>%
    select(Viral_gene_ID)

    # Combine all lists into a single data frame
    upset_data <- data.frame(Viral_gene_ID = data_M06$Viral_gene_ID,
                            Pfam = as.integer(data_M06$Viral_gene_ID %in% Pfam_list$Viral_gene_ID),
                            PHROGS = as.integer(data_M06$Viral_gene_ID %in% PHROGS_list$Viral_gene_ID),
                            geNomad = as.integer(data_M06$Viral_gene_ID %in% geNomad_list$Viral_gene_ID))

    p_annotation_upset <- upset(
                            upset_data, 
                            name='Group',
                            width_ratio=0.3,
                            c('Pfam', 'PHROGS', 'geNomad'),
                            queries = list(upset_query(set = 'Pfam', fill = '#CB1800'),
                                            upset_query(set = 'PHROGS', fill = '#00A87E'),
                                            upset_query(set = 'geNomad', fill = '#61BCEC')),
                            base_annotations=list('Shared genes between groups'=(intersection_size(counts=T, col = "black", 
                                                                                                    bar_number_threshold=1, width=0.8) +
                                                                                    scale_y_continuous(expand=expansion(mult=c(0, 0.05))) + 
                                                                                    theme(panel.grid=element_blank(),
                                                                                        panel.background = element_rect(fill = 'white'),
                                                                                        axis.text.x=element_blank(),
                                                                                        axis.text.y = element_text(color="black", size=14),
                                                                                        axis.title = element_text(color="black", size=14),
                                                                                        axis.title.x=element_blank(),
                                                                                        axis.line=element_line(colour='black')))),
                            set_sizes=(upset_set_size(geom=geom_bar(width=0.6, col = "black"),
                                                        position = 'right') + 
                                        geom_text(aes(label=after_stat(count)), hjust=-0.1, stat='count') +
                                        ylab("Nb of genes per group") +
                                        theme(panel.background =element_blank(),
                                                axis.line.x=element_line(colour='black'),
                                                axis.ticks.y=element_blank(),
                                                axis.text.y=element_blank(),
                                                axis.text.x = element_text(color="black", size=14),
                                                axis.title.x = element_text(color="black", size=14),
                                                axis.title.y=element_blank())),
                            theme = list(legend.text.align = NULL),
                            matrix=(intersection_matrix(geom=geom_point(shape='circle filled', size=3.5, stroke=0.45)) + 
                                        ylab("Database") +
                                        theme(panel.background =element_blank(),
                                            axis.line=element_blank(),
                                            axis.ticks=element_blank(),
                                            axis.title=element_text(color="black", size=14),
                                            axis.text.y = element_text(color="black", size=14),
                                            axis.text.x=element_blank())),
                            stripes=upset_stripes(geom=geom_segment(linewidth=12), colors=c('grey95', 'white')),
                            sort_sets='descending',
                            sort_intersections='descending')
}}

spacer <-  ggplot() +
                geom_blank(fill = "white") +  # Set the background color to white
                theme_void()

title <- ggdraw() + draw_label("Summarized plots generated by MVP\nModule 03 (Clustering)and 06 (Functionnal annotation)", fontface='bold')

plot_col_1 <- plot_grid(title, p_conservative_filtered_vOTUs_CheckV, p_conservative_filtered_vOTUs_length, p_taxa_vOTUs_counts,
                                ncol = 1, align = "hv", rel_heights = c(0.3, 0.4, 0.6, 0.6), labels=c('','A','B', 'C'))
plot_col_2 <- plot_grid(spacer,  p_annotation_upset, spacer,  rel_heights = c(0.2, 0.8, 0.3),
                            ncol = 1, labels=c('','D',''))
combined_plots <- plot_grid(plot_col_1, plot_col_2, align = "hv", ncol = 2)

ggsave("{output_folder}/Summarize_output_plots.pdf", plot = combined_plots, width = 20, height = 12)
    """.format(votu_table_file_path=votu_table_file_path, metadata_file_path=metadata_file_path, functional_annotation_table_file_path=functional_annotation_table_file_path, output_folder=output_folder)

    # Run the R code
    robjects.r(r_code)

def create_module_05_figures(votu_table_file_path, metadata_file_path, output_folder):
    print(f"\n\033[1m{step_counter.print_main_step()}: Generating figures for Module 05 using R...\033[0m")

    r_code = """
library(ggplot2)
library(dplyr)
library(cowplot)
library(readr)
library(ComplexUpset)
library(stringr)
library(reshape2)
library(vegan)

data = read.table("{votu_table_file_path}", h=T, sep="\t", dec=".")

checkv_data <- data %>%
  count(checkv_quality = checkv_quality) %>%
  mutate(checkv_quality = factor(checkv_quality, levels = c("Complete", "High-quality", "Medium-quality", "Low-quality", "Not-determined"))) %>%
  mutate(Factor = "checkv_quality")

# Create the box plot
p_conservative_filtered_vOTUs_CheckV <- ggplot(checkv_data, aes(x = Factor, y = n, fill = checkv_quality)) +
  geom_bar(stat="identity", color = "black", size = 1, width = 0.8) + 
  theme_minimal() +
  scale_fill_manual(values = c("white", "#D3D3D3", "#9D9D9D", "#686868", "#333333"), 
                    limits = c("Not-determined", "Low-quality", "Medium-quality", "High-quality", "Complete"),
                    name="CheckV quality") +
  coord_flip() +
  labs(y = "Number", x = "") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

length_data <- data %>%
  mutate(Length_Category = case_when(
    virus_length < 10000 ~ "<10 kb",
    virus_length >= 10000 & virus_length <= 50000 ~ "10-50 kb",
    TRUE ~ ">50 kb")) %>%
  count(Length_Category) %>%
  mutate(Length_Category = factor(Length_Category, levels = c("<10 kb", "10-50 kb", ">50 kb"))) %>%
  mutate(Factor = "Length")

p_conservative_filtered_vOTUs_length <- ggplot(length_data, aes(x = Length_Category, y = n)) +
  geom_bar(stat="identity", position= position_dodge(preserve = "single"), fill = '#D3D3D3', color = "black", size = 1) + 
  theme_minimal() +
  coord_flip() +
  labs(y = "Number", x = "Genome length") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

data <- data %>%
  mutate(Taxonomy = sapply(strsplit(as.character(taxonomy), ";"), function(x) {{
    level_5 <- ifelse(length(x) >= 5, x[5], tail(x, 1))
    if (level_5 == "Viruses") {{
      return("Unclassified")
    }} else {{
      return(level_5)
    }}
  }}))

taxa_count_data <- data %>%
  count(Taxonomy = data$Taxonomy) %>%
  mutate(Factor = "Taxonomy")
head(taxa_count_data)

# Define the color palette based on the presence of "Unclassified"
if ("Unclassified" %in% taxa_count_data$Taxonomy) {{
  # If "Unclassified" exists, use one less color than the number of unique taxa
  color_palette <- colorRampPalette(c("#3B9AB1", "#78B7C5", "#EBCC2A", "#E1AE01", "#F22300"))(length(unique(taxa_count_data$Taxonomy)) - 1)
  # Assign #D3D3D3 to Unclassified
  color_palette <- c(color_palette, "#D3D3D3")
}} else {{
  # If "Unclassified" doesn't exist, use the number of unique taxa as the number of colors
  color_palette <- colorRampPalette(c("#3B9AB1", "#78B7C5", "#EBCC2A", "#E1AE01", "#F22300"))(length(unique(taxa_count_data$Taxonomy)))
}}  

# Create the ggplot
p_taxa_vOTUs_counts <- ggplot(taxa_count_data, aes(x = Factor, y = n, fill = Taxonomy)) +
  geom_bar(position = "fill", stat = "identity", color = "black", size = 1) + 
  scale_fill_manual(values = color_palette) +
  labs(x = "", y = "Percentage (%)", fill = "Taxonomy") + 
  theme_minimal() +
  coord_flip() +
  scale_y_continuous(labels = scales::percent_format()) +
  theme(legend.justification = c(0, 0.5), 
        axis.text = element_text(color = "black", size = 14),
        axis.title = element_text(color = "black", size = 14),
        axis.ticks = element_line(size = 0.8, color = "black"),
        axis.ticks.length = unit(0.2, "cm"))

        
metadata = read.table("{metadata_file_path}", h=T, sep="\t", dec=".")

if ("Variable" %in% colnames(metadata)) {{
    metadata_subset <- metadata[, c('Sample', 'Variable')]
    selected_RPKM_columns <- c("virus_id", grep('^RPKM_', names(data), value = TRUE))
    RPKM_data <- data[selected_RPKM_columns]
    colnames(RPKM_data) <- gsub('^RPKM_', '', colnames(RPKM_data))
    RPKM_data_t <- dcast(melt(RPKM_data, id.vars = "virus_id"), variable ~ virus_id)
    RPKM_data_t <- RPKM_data_t %>% rename(Sample = variable)
    RPKM_data_t_metadata <- merge(x = metadata_subset, y = RPKM_data_t, by = "Sample")
    RPKM_data_t_metadata_bio <- RPKM_data_t_metadata[,-c(1,2)]

    MDS <- cmdscale(vegdist(RPKM_data_t_metadata_bio, method = "bray"), k = 3, eig = T, add = T )
    variance_explained <- round(MDS$eig * 100 / sum(MDS$eig), 1)
    variance_explained_first_two <- head(variance_explained, 2)
    nMDS1_label <- paste0("nMDS 1 (", variance_explained_first_two[1], "%)")
    nMDS2_label <- paste0("nMDS 2 (", variance_explained_first_two[2], "%)")
    RPKM_data_t_metadata_bio_dist <- vegdist(RPKM_data_t_metadata_bio, method = "bray")
    RPKM_data_t_metadata_bio_dist_MDS <- metaMDS(RPKM_data_t_metadata_bio_dist, distance = "bray", k = 3, trymax=1000)
    nmds_coordinates <- data.frame(RPKM_data_t_metadata_bio_dist_MDS$points)
    nmds_data <- cbind(nmds_coordinates, Variable = RPKM_data_t_metadata$Variable)

    color_palette <- colorRampPalette(c("#A36B2B", "#C6AA74", "#EDEAC2", "#94B9A7", "#2686A0"))(length(unique(RPKM_data_t_metadata$Variable)))

    p_conservative_filtered_vOTUs_nMDS <- ggplot(nmds_data, aes(x = MDS1, y = MDS2, fill = Variable)) +
                    geom_point(shape = 21, color="black", size = 5, stroke = 2) +
                    theme_bw() +
                    theme(axis.text = element_text(color = "black", size = 14),
                            axis.title = element_text(color = "black", size = 14),
                            axis.ticks = element_line(size = 0.8, color = "black"), 
                            axis.ticks.length = unit(0.2, "cm")) +
                    labs(x = nMDS1_label, y = nMDS2_label) + 
                    scale_fill_manual(values = color_palette)
}}

spacer <-  ggplot() +
                geom_blank(fill = "white") +  # Set the background color to white
                theme_void()

title <- ggdraw() + draw_label("Summarized plots generated by MVP\nModule 05 (vOTU tables)", fontface='bold')

if ("Variable" %in% colnames(metadata)) {{
    plot_col_1 <- plot_grid(title, p_conservative_filtered_vOTUs_CheckV, p_conservative_filtered_vOTUs_length, p_taxa_vOTUs_counts,
                                ncol = 1, align = "hv", rel_heights = c(0.3, 0.6, 0.6, 1, 0.5), labels=c('','A','B', 'C'))
    plot_col_2 <- plot_grid(spacer, p_conservative_filtered_vOTUs_nMDS, spacer, rel_heights = c(0.15, 0.8, 0.2),
                            ncol = 1, labels=c('','D', ''))
    combined_plots <- plot_grid(plot_col_1, plot_col_2, ncol = 2)
    print(combined_plots)
}} else {{
combined_plots <- plot_grid(title, p_conservative_filtered_vOTUs_CheckV, p_conservative_filtered_vOTUs_length, p_taxa_vOTUs_counts,
                                ncol = 1, align = "hv", rel_heights = c(0.3, 0.6, 0.6, 1, 0.5), labels=c('','A','B', 'C'))
}}
ggsave("{output_folder}/Summarize_output_plots.pdf", plot = combined_plots, width = 20, height = 12)
    """.format(votu_table_file_path=votu_table_file_path, metadata_file_path=metadata_file_path, output_folder=output_folder)

    # Run the R code
    robjects.r(r_code)

def create_module_05_06_figures(votu_table_file_path, metadata_file_path, functional_annotation_table_file_path, output_folder):
    print(f"\n\033[1m{step_counter.print_main_step()}: Generating figures for Module 05 and Module 06 using R...\033[0m")

    r_code = """
library(ggplot2)
library(dplyr)
library(cowplot)
library(readr)
library(ComplexUpset)
library(stringr)
library(reshape2)
library(vegan)

data = read.table("{votu_table_file_path}", h=T, sep="\t", dec=".")

checkv_data <- data %>%
  count(checkv_quality = checkv_quality) %>%
  mutate(checkv_quality = factor(checkv_quality, levels = c("Complete", "High-quality", "Medium-quality", "Low-quality", "Not-determined"))) %>%
  mutate(Factor = "checkv_quality")

# Create the box plot
p_conservative_filtered_vOTUs_CheckV <- ggplot(checkv_data, aes(x = Factor, y = n, fill = checkv_quality)) +
  geom_bar(stat="identity", color = "black", size = 1, width = 0.8) + 
  theme_minimal() +
  scale_fill_manual(values = c("white", "#D3D3D3", "#9D9D9D", "#686868", "#333333"), 
                    limits = c("Not-determined", "Low-quality", "Medium-quality", "High-quality", "Complete"),
                    name="CheckV quality") +
  coord_flip() +
  labs(y = "Number", x = "") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

length_data <- data %>%
  mutate(Length_Category = case_when(
    virus_length < 10000 ~ "<10 kb",
    virus_length >= 10000 & virus_length <= 50000 ~ "10-50 kb",
    TRUE ~ ">50 kb")) %>%
  count(Length_Category) %>%
  mutate(Length_Category = factor(Length_Category, levels = c("<10 kb", "10-50 kb", ">50 kb"))) %>%
  mutate(Factor = "Length")

p_conservative_filtered_vOTUs_length <- ggplot(length_data, aes(x = Length_Category, y = n)) +
  geom_bar(stat="identity", position= position_dodge(preserve = "single"), fill = '#D3D3D3', color = "black", size = 1) + 
  theme_minimal() +
  coord_flip() +
  labs(y = "Number", x = "Genome length") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

data <- data %>%
  mutate(Taxonomy = sapply(strsplit(as.character(taxonomy), ";"), function(x) {{
    level_5 <- ifelse(length(x) >= 5, x[5], tail(x, 1))
    if (level_5 == "Viruses") {{
      return("Unclassified")
    }} else {{
      return(level_5)
    }}
  }}))

taxa_count_data <- data %>%
  count(Taxonomy = data$Taxonomy) %>%
  mutate(Factor = "Taxonomy")
head(taxa_count_data)

# Define the color palette based on the presence of "Unclassified"
if ("Unclassified" %in% taxa_count_data$Taxonomy) {{
  # If "Unclassified" exists, use one less color than the number of unique taxa
  color_palette <- colorRampPalette(c("#3B9AB1", "#78B7C5", "#EBCC2A", "#E1AE01", "#F22300"))(length(unique(taxa_count_data$Taxonomy)) - 1)
  # Assign #D3D3D3 to Unclassified
  color_palette <- c(color_palette, "#D3D3D3")
}} else {{
  # If "Unclassified" doesn't exist, use the number of unique taxa as the number of colors
  color_palette <- colorRampPalette(c("#3B9AB1", "#78B7C5", "#EBCC2A", "#E1AE01", "#F22300"))(length(unique(taxa_count_data$Taxonomy)))
}}  

# Create the ggplot
p_taxa_vOTUs_counts <- ggplot(taxa_count_data, aes(x = Factor, y = n, fill = Taxonomy)) +
  geom_bar(position = "fill", stat = "identity", color = "black", size = 1) + 
  scale_fill_manual(values = color_palette) +
  labs(x = "", y = "Percentage (%)", fill = "Taxonomy") + 
  theme_minimal() +
  coord_flip() +
  scale_y_continuous(labels = scales::percent_format()) +
  theme(legend.justification = c(0, 0.5), 
        axis.text = element_text(color = "black", size = 14),
        axis.title = element_text(color = "black", size = 14),
        axis.ticks = element_line(size = 0.8, color = "black"),
        axis.ticks.length = unit(0.2, "cm"))

        
metadata = read.table("{metadata_file_path}", h=T, sep="\t", dec=".")

if ("Variable" %in% colnames(metadata)) {{
    metadata_subset <- metadata[, c('Sample', 'Variable')]
    selected_RPKM_columns <- c("virus_id", grep('^RPKM_', names(data), value = TRUE))
    RPKM_data <- data[selected_RPKM_columns]
    colnames(RPKM_data) <- gsub('^RPKM_', '', colnames(RPKM_data))
    RPKM_data_t <- dcast(melt(RPKM_data, id.vars = "virus_id"), variable ~ virus_id)
    RPKM_data_t <- RPKM_data_t %>% rename(Sample = variable)
    RPKM_data_t_metadata <- merge(x = metadata_subset, y = RPKM_data_t, by = "Sample")
    RPKM_data_t_metadata_bio <- RPKM_data_t_metadata[,-c(1,2)]

    MDS <- cmdscale(vegdist(RPKM_data_t_metadata_bio, method = "bray"), k = 3, eig = T, add = T )
    variance_explained <- round(MDS$eig * 100 / sum(MDS$eig), 1)
    variance_explained_first_two <- head(variance_explained, 2)
    nMDS1_label <- paste0("nMDS 1 (", variance_explained_first_two[1], "%)")
    nMDS2_label <- paste0("nMDS 2 (", variance_explained_first_two[2], "%)")
    RPKM_data_t_metadata_bio_dist <- vegdist(RPKM_data_t_metadata_bio, method = "bray")
    RPKM_data_t_metadata_bio_dist_MDS <- metaMDS(RPKM_data_t_metadata_bio_dist, distance = "bray", k = 3, trymax=1000)
    nmds_coordinates <- data.frame(RPKM_data_t_metadata_bio_dist_MDS$points)
    nmds_data <- cbind(nmds_coordinates, Variable = RPKM_data_t_metadata$Variable)

    color_palette <- colorRampPalette(c("#A36B2B", "#C6AA74", "#EDEAC2", "#94B9A7", "#2686A0"))(length(unique(RPKM_data_t_metadata$Variable)))

    p_conservative_filtered_vOTUs_nMDS <- ggplot(nmds_data, aes(x = MDS1, y = MDS2, fill = Variable)) +
                    geom_point(shape = 21, color="black", size = 5, stroke = 2) +
                    theme_bw() +
                    theme(axis.text = element_text(color = "black", size = 14),
                            axis.title = element_text(color = "black", size = 14),
                            axis.ticks = element_line(size = 0.8, color = "black"), 
                            axis.ticks.length = unit(0.2, "cm")) +
                    labs(x = nMDS1_label, y = nMDS2_label) + 
                    scale_fill_manual(values = color_palette)
}}

if ("_ADS_" %in% str_extract("{functional_annotation_table_file_path}", "_ADS_")) {{
    data_M06 <- readr::read_csv("{functional_annotation_table_file_path}", col_types = cols(ADS_Defense_type = col_character()))
    data_M06$PHROGS_Category <- ifelse(is.na(data_M06$PHROGS_Category), "unknown", data_M06$PHROGS_Category)
    data_M06$PFAM_Annotation <- ifelse(is.na(data_M06$PFAM_Annotation), "unknown", data_M06$PFAM_Annotation)
    data_M06$ADS_Defense_type <- ifelse(is.na(data_M06$ADS_Defense_type), "unknown", data_M06$ADS_Defense_type)
    # Initialize lists for each annotation method
    ADS_list <- data.frame(Viral_gene_ID = character(0))
    Pfam_list <- data.frame(Viral_gene_ID = character(0))
    PHROGS_list <- data.frame(Viral_gene_ID = character(0))
    geNomad_list <- data.frame(Viral_gene_ID = character(0))

    # Filter data for each annotation method and populate the lists
    ADS_list <- data_M06 %>%
    filter(ADS_Defense_type != "unknown" & ADS_Defense_type != "Unknown") %>%
    select(Viral_gene_ID)

    # Filter out rows based on PFAM_Annotation column
    Pfam_list <- data_M06 %>%
    filter(!grepl(paste(c("unknown", "Unknown", "Uncharacterized"), collapse = "|"), PFAM_Annotation)) %>%
    select(Viral_gene_ID)

    PHROGS_list <- data_M06 %>%
    filter(PHROGS_Category != "unknown" & PHROGS_Category != "Unknown") %>%
    select(Viral_gene_ID)

    geNomad_list <- data_M06 %>%
    filter(GENOMAD_Annotation != "unknown" & GENOMAD_Annotation != "Unknown") %>%
    select(Viral_gene_ID)

    # Combine all lists into a single data frame
    upset_data <- data.frame(Viral_gene_ID = data_M06$Viral_gene_ID,
                            ADS = as.integer(data_M06$Viral_gene_ID %in% ADS_list$Viral_gene_ID),
                            Pfam = as.integer(data_M06$Viral_gene_ID %in% Pfam_list$Viral_gene_ID),
                            PHROGS = as.integer(data_M06$Viral_gene_ID %in% PHROGS_list$Viral_gene_ID),
                            geNomad = as.integer(data_M06$Viral_gene_ID %in% geNomad_list$Viral_gene_ID))

    p_annotation_upset <- upset(
                            upset_data, 
                            name='Group',
                            width_ratio=0.3,
                            c('ADS', 'Pfam', 'PHROGS', 'geNomad'),
                            queries = list(upset_query(set = 'ADS', fill = '#EFE32A'),
                                            upset_query(set = 'Pfam', fill = '#CB1800'),
                                            upset_query(set = 'PHROGS', fill = '#00A87E'),
                                            upset_query(set = 'geNomad', fill = '#61BCEC')),
                            base_annotations=list('Shared genes between groups'=(intersection_size(counts=T, col = "black", 
                                                                                                    bar_number_threshold=1, width=0.8) +
                                                                                    scale_y_continuous(expand=expansion(mult=c(0, 0.05))) + 
                                                                                    theme(panel.grid=element_blank(),
                                                                                        panel.background = element_rect(fill = 'white'),
                                                                                        axis.text.x=element_blank(),
                                                                                        axis.text.y = element_text(color="black", size=14),
                                                                                        axis.title = element_text(color="black", size=14),
                                                                                        axis.title.x=element_blank(),
                                                                                        axis.line=element_line(colour='black')))),
                            set_sizes=(upset_set_size(geom=geom_bar(width=0.6, col = "black"),
                                                        position = 'right') + 
                                        geom_text(aes(label=after_stat(count)), hjust=-0.1, stat='count') +
                                        ylab("Nb of genes per group") +
                                        expand_limits(y=7000) +
                                        theme(panel.background =element_blank(),
                                                axis.line.x=element_line(colour='black'),
                                                axis.ticks.y=element_blank(),
                                                axis.text.y=element_blank(),
                                                axis.text.x = element_text(color="black", size=14),
                                                axis.title.x = element_text(color="black", size=14),
                                                axis.title.y=element_blank())),
                            theme = list(legend.text.align = NULL),
                            matrix=(intersection_matrix(geom=geom_point(shape='circle filled', size=3.5, stroke=0.45)) + 
                                        ylab("Database") +
                                        theme(panel.background =element_blank(),
                                            axis.line=element_blank(),
                                            axis.ticks=element_blank(),
                                            axis.title=element_text(color="black", size=14),
                                            axis.text.y = element_text(color="black", size=14),
                                            axis.text.x=element_blank())),
                            stripes=upset_stripes(geom=geom_segment(linewidth=12), colors=c('grey95', 'white')),
                            sort_sets='descending',
                            sort_intersections='descending')
}} else {{
    data_M06 <- readr::read_csv("{functional_annotation_table_file_path}")
    data_M06$PHROGS_Category <- ifelse(is.na(data_M06$PHROGS_Category), "unknown", data_M06$PHROGS_Category)
    data_M06$PFAM_Annotation <- ifelse(is.na(data_M06$PFAM_Annotation), "unknown", data_M06$PFAM_Annotation)
    # Initialize lists for each annotation method
    Pfam_list <- data.frame(Viral_gene_ID = character(0))
    PHROGS_list <- data.frame(Viral_gene_ID = character(0))
    geNomad_list <- data.frame(Viral_gene_ID = character(0))

    # Filter out rows based on PFAM_Annotation column
    Pfam_list <- data_M06 %>%
    filter(!grepl(paste(c("unknown", "Unknown", "Uncharacterized"), collapse = "|"), PFAM_Annotation)) %>%
    select(Viral_gene_ID)

    PHROGS_list <- data_M06 %>%
    filter(PHROGS_Category != "unknown" & PHROGS_Category != "Unknown") %>%
    select(Viral_gene_ID)

    geNomad_list <- data_M06 %>%
    filter(GENOMAD_Annotation != "unknown" & GENOMAD_Annotation != "Unknown") %>%
    select(Viral_gene_ID)

    # Combine all lists into a single data frame
    upset_data <- data.frame(Viral_gene_ID = data_M06$Viral_gene_ID,
                            Pfam = as.integer(data_M06$Viral_gene_ID %in% Pfam_list$Viral_gene_ID),
                            PHROGS = as.integer(data_M06$Viral_gene_ID %in% PHROGS_list$Viral_gene_ID),
                            geNomad = as.integer(data_M06$Viral_gene_ID %in% geNomad_list$Viral_gene_ID))

    p_annotation_upset <- upset(
                            upset_data, 
                            name='Group',
                            width_ratio=0.3,
                            c('Pfam', 'PHROGS', 'geNomad'),
                            queries = list(upset_query(set = 'Pfam', fill = '#CB1800'),
                                            upset_query(set = 'PHROGS', fill = '#00A87E'),
                                            upset_query(set = 'geNomad', fill = '#61BCEC')),
                            base_annotations=list('Shared genes between groups'=(intersection_size(counts=T, col = "black", 
                                                                                                    bar_number_threshold=1, width=0.8) +
                                                                                    scale_y_continuous(expand=expansion(mult=c(0, 0.05))) + 
                                                                                    theme(panel.grid=element_blank(),
                                                                                        panel.background = element_rect(fill = 'white'),
                                                                                        axis.text.x=element_blank(),
                                                                                        axis.text.y = element_text(color="black", size=14),
                                                                                        axis.title = element_text(color="black", size=14),
                                                                                        axis.title.x=element_blank(),
                                                                                        axis.line=element_line(colour='black')))),
                            set_sizes=(upset_set_size(geom=geom_bar(width=0.6, col = "black"),
                                                        position = 'right') + 
                                        geom_text(aes(label=after_stat(count)), hjust=-0.1, stat='count') +
                                        ylab("Nb of genes per group") +
                                        theme(panel.background =element_blank(),
                                                axis.line.x=element_line(colour='black'),
                                                axis.ticks.y=element_blank(),
                                                axis.text.y=element_blank(),
                                                axis.text.x = element_text(color="black", size=14),
                                                axis.title.x = element_text(color="black", size=14),
                                                axis.title.y=element_blank())),
                            theme = list(legend.text.align = NULL),
                            matrix=(intersection_matrix(geom=geom_point(shape='circle filled', size=3.5, stroke=0.45)) + 
                                        ylab("Database") +
                                        theme(panel.background =element_blank(),
                                            axis.line=element_blank(),
                                            axis.ticks=element_blank(),
                                            axis.title=element_text(color="black", size=14),
                                            axis.text.y = element_text(color="black", size=14),
                                            axis.text.x=element_blank())),
                            stripes=upset_stripes(geom=geom_segment(linewidth=12), colors=c('grey95', 'white')),
                            sort_sets='descending',
                            sort_intersections='descending')
}}

spacer <-  ggplot() +
                geom_blank(fill = "white") +  # Set the background color to white
                theme_void()

title <- ggdraw() + draw_label("Summarized plots generated by MVP\nModule 05 (vOTU tables)and 06 (Functionnal annotation)", fontface='bold')

if ("Variable" %in% colnames(metadata)) {{
    plot_col_1 <- plot_grid(title, p_conservative_filtered_vOTUs_CheckV, p_conservative_filtered_vOTUs_length, p_taxa_vOTUs_counts,
                                ncol = 1, align = "hv", rel_heights = c(0.3, 0.6, 0.6, 1, 0.5), labels=c('','A','B', 'C'))
    plot_col_2 <- plot_grid(spacer, p_conservative_filtered_vOTUs_nMDS, p_annotation_upset, rel_heights = c(0.2, 0.8, 0.8),
                            ncol = 1, labels=c('','D','E'))
    combined_plots <- plot_grid(plot_col_1, plot_col_2, ncol = 2)
}} else {{
    plot_col_1 <- plot_grid(title, p_conservative_filtered_vOTUs_CheckV, p_conservative_filtered_vOTUs_length, p_taxa_vOTUs_counts,
                                ncol = 1, align = "hv", rel_heights = c(0.3, 0.6, 0.6, 1, 0.5), labels=c('','A','B', 'C'))
    plot_col_2 <- plot_grid(spacer,  p_annotation_upset, spacer,  rel_heights = c(0.15, 0.8, 0.2),
                            ncol = 1, labels=c('','D',''))
    combined_plots <- plot_grid(plot_col_1, plot_col_2, ncol = 2)
}}
ggsave("{output_folder}/Summarize_output_plots.pdf", plot = combined_plots, width = 20, height = 12)
    """.format(votu_table_file_path=votu_table_file_path, metadata_file_path=metadata_file_path, functional_annotation_table_file_path=functional_annotation_table_file_path, output_folder=output_folder)

    # Run the R code
    robjects.r(r_code)

def create_module_07_figures(votu_table_file_path, metadata_file_path, output_folder):
    print(f"\n\033[1m{step_counter.print_main_step()}: Generating figures for Module 07 using R...\033[0m")

    # Define R code
    r_code = """
library(ggplot2)
library(dplyr)
library(cowplot)
library(readr)
library(ComplexUpset)
library(stringr)
library(reshape2)
library(vegan)

data = read.table("{votu_table_file_path}", h=T, sep="\t", dec=".")

# Add Variable_Type column to vBins_count_data_M07
vBins_count_data <- data %>%
                    count(Type = data$Type) %>%
                    mutate(x = "Type")
vBins_count_data$Type <- factor(vBins_count_data$Type, levels = c("vBin", "Unbinned_Contig"),
                                    labels = c("vBin", "Unbinned\ncontig"))

p_filtered_vBins <- ggplot(vBins_count_data, aes(x = x, y = n, fill = Type)) +
  geom_bar(stat="identity", color = "black", size = 1, width = 0.5) + 
  theme_minimal() +
  scale_fill_manual(values = c("white", "#D3D3D3"), limits = c("Unbinned\ncontig", "vBin")) +
  coord_flip() +
  labs(x = "", y = "Number") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

checkv_data <- data %>%
  group_by(Type) %>%
  count(checkv_quality = checkv_quality) %>%
  mutate(checkv_quality = factor(checkv_quality, levels = c("Complete", "High-quality", "Medium-quality", "Low-quality"))) %>%
  mutate(Factor = "checkv_quality")
checkv_data$Type <- factor(checkv_data$Type, levels = c("vBin", "Unbinned_Contig"),
                                labels = c("vBin", "Unbinned\ncontig"))

# Create the box plot
p_conservative_filtered_vBins_CheckV <- ggplot(checkv_data, aes(x = Type, y = n, fill = checkv_quality)) +
  geom_bar(stat="identity", color = "black", size = 1, width = 0.8) + 
  theme_minimal() +
  scale_fill_manual(values = c("#D3D3D3", "#9D9D9D", "#686868", "#333333"), 
                    limits = c("Low-quality", "Medium-quality", "High-quality", "Complete"),
                    name="CheckV quality") +
  coord_flip() +
  labs(y = "Number", x = "") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

length_data <- data %>%
  group_by(Type) %>%
  mutate(Length_Category = case_when(
    virus_length < 10000 ~ "<10 kb",
    virus_length >= 10000 & virus_length <= 50000 ~ "10-50 kb",
    TRUE ~ ">50 kb")) %>%
  count(Length_Category) %>%
  mutate(Length_Category = factor(Length_Category, levels = c("<10 kb", "10-50 kb", ">50 kb"))) %>%
  mutate(Factor = "Length")
length_data$Type <- factor(length_data$Type, levels = c("vBin", "Unbinned_Contig"),
                           labels = c("vBin", "Unbinned\ncontig"))

p_conservative_filtered_vBins_length <- ggplot(length_data, aes(x = Length_Category, y = n, fill = Type)) +
  geom_bar(stat="identity", position= position_dodge(preserve = "single"), color = "black", size = 1) + 
  theme_minimal() +
  scale_fill_manual(values = c("white", "#D3D3D3"), limits = c("Unbinned\ncontig", "vBin")) +
  coord_flip() +
  labs(y = "Number", x = "Genome length") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

data <- data %>%
  mutate(Taxonomy = sapply(strsplit(as.character(taxonomy), ";"), function(x) {{
    level_5 <- ifelse(length(x) >= 5, x[5], tail(x, 1))
    if (level_5 == "Viruses") {{
      return("Unclassified")
    }} else {{
      return(level_5)
    }}
  }}))

taxa_count_data <- data %>%
  count(Taxonomy = data$Taxonomy) %>%
  mutate(Factor = "Taxonomy")
head(taxa_count_data)

# Define the color palette based on the presence of "Unclassified"
if ("Unclassified" %in% taxa_count_data$Taxonomy) {{
  # If "Unclassified" exists, use one less color than the number of unique taxa
  color_palette <- colorRampPalette(c("#3B9AB1", "#78B7C5", "#EBCC2A", "#E1AE01", "#F22300"))(length(unique(taxa_count_data$Taxonomy)) - 1)
  # Assign #D3D3D3 to Unclassified
  color_palette <- c(color_palette, "#D3D3D3")
}} else {{
  # If "Unclassified" doesn't exist, use the number of unique taxa as the number of colors
  color_palette <- colorRampPalette(c("#3B9AB1", "#78B7C5", "#EBCC2A", "#E1AE01", "#F22300"))(length(unique(taxa_count_data$Taxonomy)))
}}  

# Create the ggplot
p_taxa_vBins_counts <- ggplot(taxa_count_data, aes(x = Factor, y = n, fill = Taxonomy)) +
  geom_bar(position = "fill", stat = "identity", color = "black", size = 1) + 
  scale_fill_manual(values = color_palette) +
  labs(x = "", y = "Percentage (%)", fill = "Taxonomy") + 
  theme_minimal() +
  coord_flip() +
  scale_y_continuous(labels = scales::percent_format()) +
  theme(legend.justification = c(0, 0.5), 
        axis.text = element_text(color = "black", size = 14),
        axis.title = element_text(color = "black", size = 14),
        axis.ticks = element_line(size = 0.8, color = "black"),
        axis.ticks.length = unit(0.2, "cm"))

        
metadata = read.table("{metadata_file_path}", h=T, sep="\t", dec=".")

if ("Variable" %in% colnames(metadata)) {{
    metadata_subset <- metadata[, c('Sample', 'Variable')]
    selected_RPKM_columns <- c("virus_id", grep('^RPKM_', names(data), value = TRUE))
    RPKM_data <- data[selected_RPKM_columns]
    colnames(RPKM_data) <- gsub('^RPKM_', '', colnames(RPKM_data))
    RPKM_data_t <- dcast(melt(RPKM_data, id.vars = "virus_id"), variable ~ virus_id)
    RPKM_data_t <- RPKM_data_t %>% rename(Sample = variable)
    RPKM_data_t_metadata <- merge(x = metadata_subset, y = RPKM_data_t, by = "Sample")
    RPKM_data_t_metadata_bio <- RPKM_data_t_metadata[,-c(1,2)]

    MDS <- cmdscale(vegdist(RPKM_data_t_metadata_bio, method = "bray"), k = 3, eig = T, add = T )
    variance_explained <- round(MDS$eig * 100 / sum(MDS$eig), 1)
    variance_explained_first_two <- head(variance_explained, 2)
    nMDS1_label <- paste0("nMDS 1 (", variance_explained_first_two[1], "%)")
    nMDS2_label <- paste0("nMDS 2 (", variance_explained_first_two[2], "%)")
    RPKM_data_t_metadata_bio_dist <- vegdist(RPKM_data_t_metadata_bio, method = "bray")
    RPKM_data_t_metadata_bio_dist_MDS <- metaMDS(RPKM_data_t_metadata_bio_dist, distance = "bray", k = 3, trymax=1000)
    nmds_coordinates <- data.frame(RPKM_data_t_metadata_bio_dist_MDS$points)
    nmds_data <- cbind(nmds_coordinates, Variable = RPKM_data_t_metadata$Variable)

    color_palette <- colorRampPalette(c("#A36B2B", "#C6AA74", "#EDEAC2", "#94B9A7", "#2686A0"))(length(unique(RPKM_data_t_metadata$Variable)))

    p_conservative_filtered_vBins_nMDS <- ggplot(nmds_data, aes(x = MDS1, y = MDS2, fill = Variable)) +
                    geom_point(shape = 21, color="black", size = 5, stroke = 2) +
                    theme_bw() +
                    theme(axis.text = element_text(color = "black", size = 14),
                            axis.title = element_text(color = "black", size = 14),
                            axis.ticks = element_line(size = 0.8, color = "black"), 
                            axis.ticks.length = unit(0.2, "cm")) +
                    labs(x = nMDS1_label, y = nMDS2_label) + 
                    scale_fill_manual(values = color_palette)


}} else {{
    # Continue execution if metadata does not have a column named "Variable"
    next
}}

if ("Variable" %in% colnames(metadata)) {{
    spacer <-  ggplot() +
                geom_blank(fill = "white") +  # Set the background color to white
                theme_void()

    title <- ggdraw() + draw_label("Summarized plots generated by MVP\nModule 07 (Binning)", fontface='bold')
    plot_col_1 <- plot_grid(title, p_filtered_vBins, p_conservative_filtered_vBins_CheckV, p_conservative_filtered_vBins_length, p_taxa_vBins_counts,
                                ncol = 1, align = "hv", rel_heights = c(0.3, 0.6, 0.6, 1, 0.5), labels=c('','A','B', 'C', 'D'))
    plot_col_2 <- plot_grid(spacer, p_conservative_filtered_vBins_nMDS, spacer, rel_heights = c(0.1, 0.8, 0.3),
                            ncol = 1, labels=c('','E', ''))
    combined_plots <- plot_grid(plot_col_1, plot_col_2, ncol = 2)
    print(combined_plots)
}} else {{
title <- ggdraw() + draw_label("Summarized plots generated by MVP\nModule 07 (Binning)", fontface='bold')
combined_plots <- plot_grid(title, p_filtered_vBins, p_conservative_filtered_vBins_CheckV, p_conservative_filtered_vBins_length, p_taxa_vBins_counts,
                            ncol = 1, align = "hv", rel_heights = c(0.3, 0.6, 0.6, 1, 0.5), labels=c('','A','B', 'C', 'D'))
}}

ggsave("{output_folder}/Summarize_output_plots.pdf", plot = combined_plots, width = 20, height = 12)
    """.format(votu_table_file_path=votu_table_file_path, metadata_file_path=metadata_file_path, output_folder=output_folder)

    # Run the R code
    robjects.r(r_code)

def create_module_06_07_figures(votu_table_file_path, functional_annotation_table_file_path, metadata_file_path, output_folder):
    print(f"\n\033[1m{step_counter.print_main_step()}: Generating figures for Module 06 and Module 07 using R...\033[0m")

    # Define R code
    r_code = """
sink("/dev/null")
library(ggplot2)
library(dplyr)
library(cowplot)
library(readr)
library(ComplexUpset)
library(stringr)
library(reshape2)
library(vegan)

data = read.table("{votu_table_file_path}", h=T, sep="\t", dec=".")

# Add Variable_Type column to vBins_count_data_M07
vBins_count_data <- data %>%
                    count(Type = data$Type) %>%
                    mutate(x = "Type")
vBins_count_data$Type <- factor(vBins_count_data$Type, levels = c("vBin", "Unbinned_Contig"),
                                    labels = c("vBin", "Unbinned\ncontig"))

p_filtered_vBins <- ggplot(vBins_count_data, aes(x = x, y = n, fill = Type)) +
  geom_bar(stat="identity", color = "black", size = 1, width = 0.5) + 
  theme_minimal() +
  scale_fill_manual(values = c("white", "#D3D3D3"), limits = c("Unbinned\ncontig", "vBin")) +
  coord_flip() +
  labs(x = "", y = "Number") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

checkv_data <- data %>%
  group_by(Type) %>%
  count(checkv_quality = checkv_quality) %>%
  mutate(checkv_quality = factor(checkv_quality, levels = c("Complete", "High-quality", "Medium-quality", "Low-quality"))) %>%
  mutate(Factor = "checkv_quality")
checkv_data$Type <- factor(checkv_data$Type, levels = c("vBin", "Unbinned_Contig"),
                                labels = c("vBin", "Unbinned\ncontig"))

# Create the box plot
p_conservative_filtered_vBins_CheckV <- ggplot(checkv_data, aes(x = Type, y = n, fill = checkv_quality)) +
  geom_bar(stat="identity", color = "black", size = 1, width = 0.8) + 
  theme_minimal() +
  scale_fill_manual(values = c("#D3D3D3", "#9D9D9D", "#686868", "#333333"), 
                    limits = c("Low-quality", "Medium-quality", "High-quality", "Complete"),
                    name="CheckV quality") +
  coord_flip() +
  labs(y = "Number", x = "") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

length_data <- data %>%
  group_by(Type) %>%
  mutate(Length_Category = case_when(
    virus_length < 10000 ~ "<10 kb",
    virus_length >= 10000 & virus_length <= 50000 ~ "10-50 kb",
    TRUE ~ ">50 kb")) %>%
  count(Length_Category) %>%
  mutate(Length_Category = factor(Length_Category, levels = c("<10 kb", "10-50 kb", ">50 kb"))) %>%
  mutate(Factor = "Length")
length_data$Type <- factor(length_data$Type, levels = c("vBin", "Unbinned_Contig"),
                           labels = c("vBin", "Unbinned\ncontig"))

p_conservative_filtered_vBins_length <- ggplot(length_data, aes(x = Length_Category, y = n, fill = Type)) +
  geom_bar(stat="identity", position= position_dodge(preserve = "single"), color = "black", size = 1) + 
  theme_minimal() +
  scale_fill_manual(values = c("white", "#D3D3D3"), limits = c("Unbinned\ncontig", "vBin")) +
  coord_flip() +
  labs(y = "Number", x = "Genome length") + 
  theme(legend.justification = c(0,0.5), 
        axis.text = element_text(color="black", size=14),
        axis.title = element_text(color="black", size=14),
        axis.ticks = element_line(size = 0.8, color="black"), axis.ticks.length = unit(0.2, "cm"))

data <- data %>%
  mutate(Taxonomy = sapply(strsplit(as.character(taxonomy), ";"), function(x) {{
    level_5 <- ifelse(length(x) >= 5, x[5], tail(x, 1))
    if (level_5 == "Viruses") {{
      return("Unclassified")
    }} else {{
      return(level_5)
    }}
  }}))

taxa_count_data <- data %>%
  count(Taxonomy = data$Taxonomy) %>%
  mutate(Factor = "Taxonomy")
head(taxa_count_data)

# Define the color palette based on the presence of "Unclassified"
if ("Unclassified" %in% taxa_count_data$Taxonomy) {{
  # If "Unclassified" exists, use one less color than the number of unique taxa
  color_palette <- colorRampPalette(c("#3B9AB1", "#78B7C5", "#EBCC2A", "#E1AE01", "#F22300"))(length(unique(taxa_count_data$Taxonomy)) - 1)
  # Assign #D3D3D3 to Unclassified
  color_palette <- c(color_palette, "#D3D3D3")
}} else {{
  # If "Unclassified" doesn't exist, use the number of unique taxa as the number of colors
  color_palette <- colorRampPalette(c("#3B9AB1", "#78B7C5", "#EBCC2A", "#E1AE01", "#F22300"))(length(unique(taxa_count_data$Taxonomy)))
}}  

# Create the ggplot
p_taxa_vBins_counts <- ggplot(taxa_count_data, aes(x = Factor, y = n, fill = Taxonomy)) +
  geom_bar(position = "fill", stat = "identity", color = "black", size = 1) + 
  scale_fill_manual(values = color_palette) +
  labs(x = "", y = "Percentage (%)", fill = "Taxonomy") + 
  theme_minimal() +
  coord_flip() +
  scale_y_continuous(labels = scales::percent_format()) +
  theme(legend.justification = c(0, 0.5), 
        axis.text = element_text(color = "black", size = 14),
        axis.title = element_text(color = "black", size = 14),
        axis.ticks = element_line(size = 0.8, color = "black"),
        axis.ticks.length = unit(0.2, "cm"))

        
metadata = read.table("{metadata_file_path}", h=T, sep="\t", dec=".")

if ("Variable" %in% colnames(metadata)) {{
    metadata_subset <- metadata[, c('Sample', 'Variable')]
    selected_RPKM_columns <- c("virus_id", grep('^RPKM_', names(data), value = TRUE))
    RPKM_data <- data[selected_RPKM_columns]
    colnames(RPKM_data) <- gsub('^RPKM_', '', colnames(RPKM_data))
    RPKM_data_t <- dcast(melt(RPKM_data, id.vars = "virus_id"), variable ~ virus_id)
    RPKM_data_t <- RPKM_data_t %>% rename(Sample = variable)
    RPKM_data_t_metadata <- merge(x = metadata_subset, y = RPKM_data_t, by = "Sample")
    RPKM_data_t_metadata_bio <- RPKM_data_t_metadata[,-c(1,2)]

    MDS <- cmdscale(vegdist(RPKM_data_t_metadata_bio, method = "bray"), k = 3, eig = T, add = T )
    variance_explained <- round(MDS$eig * 100 / sum(MDS$eig), 1)
    variance_explained_first_two <- head(variance_explained, 2)
    nMDS1_label <- paste0("nMDS 1 (", variance_explained_first_two[1], "%)")
    nMDS2_label <- paste0("nMDS 2 (", variance_explained_first_two[2], "%)")
    RPKM_data_t_metadata_bio_dist <- vegdist(RPKM_data_t_metadata_bio, method = "bray")
    RPKM_data_t_metadata_bio_dist_MDS <- metaMDS(RPKM_data_t_metadata_bio_dist, distance = "bray", k = 3, trymax=1000)
    nmds_coordinates <- data.frame(RPKM_data_t_metadata_bio_dist_MDS$points)
    nmds_data <- cbind(nmds_coordinates, Variable = RPKM_data_t_metadata$Variable)

    color_palette <- colorRampPalette(c("#A36B2B", "#C6AA74", "#EDEAC2", "#94B9A7", "#2686A0"))(length(unique(RPKM_data_t_metadata$Variable)))

    p_conservative_filtered_vBins_nMDS <- ggplot(nmds_data, aes(x = MDS1, y = MDS2, fill = Variable)) +
                    geom_point(shape = 21, color="black", size = 5, stroke = 2) +
                    theme_bw() +
                    theme(axis.text = element_text(color = "black", size = 14),
                            axis.title = element_text(color = "black", size = 14),
                            axis.ticks = element_line(size = 0.8, color = "black"), 
                            axis.ticks.length = unit(0.2, "cm")) +
                    labs(x = nMDS1_label, y = nMDS2_label) + 
                    scale_fill_manual(values = color_palette)


}}

if ("_ADS_" %in% str_extract("{functional_annotation_table_file_path}", "_ADS_")) {{
    data_M06 <- readr::read_csv("{functional_annotation_table_file_path}", col_types = cols(ADS_Defense_type = col_character()))
    data_M06$PHROGS_Category <- ifelse(is.na(data_M06$PHROGS_Category), "unknown", data_M06$PHROGS_Category)
    data_M06$PFAM_Annotation <- ifelse(is.na(data_M06$PFAM_Annotation), "unknown", data_M06$PFAM_Annotation)
    data_M06$ADS_Defense_type <- ifelse(is.na(data_M06$ADS_Defense_type), "unknown", data_M06$ADS_Defense_type)
    # Initialize lists for each annotation method
    ADS_list <- data.frame(Viral_gene_ID = character(0))
    Pfam_list <- data.frame(Viral_gene_ID = character(0))
    PHROGS_list <- data.frame(Viral_gene_ID = character(0))
    geNomad_list <- data.frame(Viral_gene_ID = character(0))

    # Filter data for each annotation method and populate the lists
    ADS_list <- data_M06 %>%
    filter(ADS_Defense_type != "unknown" & ADS_Defense_type != "Unknown") %>%
    select(Viral_gene_ID)

    # Filter out rows based on PFAM_Annotation column
    Pfam_list <- data_M06 %>%
    filter(!grepl(paste(c("unknown", "Unknown", "Uncharacterized"), collapse = "|"), PFAM_Annotation)) %>%
    select(Viral_gene_ID)

    PHROGS_list <- data_M06 %>%
    filter(PHROGS_Category != "unknown" & PHROGS_Category != "Unknown") %>%
    select(Viral_gene_ID)

    geNomad_list <- data_M06 %>%
    filter(GENOMAD_Annotation != "unknown" & GENOMAD_Annotation != "Unknown") %>%
    select(Viral_gene_ID)

    # Combine all lists into a single data frame
    upset_data <- data.frame(Viral_gene_ID = data_M06$Viral_gene_ID,
                            ADS = as.integer(data_M06$Viral_gene_ID %in% ADS_list$Viral_gene_ID),
                            Pfam = as.integer(data_M06$Viral_gene_ID %in% Pfam_list$Viral_gene_ID),
                            PHROGS = as.integer(data_M06$Viral_gene_ID %in% PHROGS_list$Viral_gene_ID),
                            geNomad = as.integer(data_M06$Viral_gene_ID %in% geNomad_list$Viral_gene_ID))

    p_annotation_upset <- upset(
                            upset_data, 
                            name='Group',
                            width_ratio=0.3,
                            c('ADS', 'Pfam', 'PHROGS', 'geNomad'),
                            queries = list(upset_query(set = 'ADS', fill = '#EFE32A'),
                                            upset_query(set = 'Pfam', fill = '#CB1800'),
                                            upset_query(set = 'PHROGS', fill = '#00A87E'),
                                            upset_query(set = 'geNomad', fill = '#61BCEC')),
                            base_annotations=list('Shared genes between groups'=(intersection_size(counts=T, col = "black", 
                                                                                                    bar_number_threshold=1, width=0.8) +
                                                                                    scale_y_continuous(expand=expansion(mult=c(0, 0.05))) + 
                                                                                    theme(panel.grid=element_blank(),
                                                                                        panel.background = element_rect(fill = 'white'),
                                                                                        axis.text.x=element_blank(),
                                                                                        axis.text.y = element_text(color="black", size=14),
                                                                                        axis.title = element_text(color="black", size=14),
                                                                                        axis.title.x=element_blank(),
                                                                                        axis.line=element_line(colour='black')))),
                            set_sizes=(upset_set_size(geom=geom_bar(width=0.6, col = "black"),
                                                        position = 'right') + 
                                        geom_text(aes(label=after_stat(count)), hjust=-0.1, stat='count') +
                                        ylab("Nb of genes per group") +
                                        expand_limits(y=7000) +
                                        theme(panel.background =element_blank(),
                                                axis.line.x=element_line(colour='black'),
                                                axis.ticks.y=element_blank(),
                                                axis.text.y=element_blank(),
                                                axis.text.x = element_text(color="black", size=14),
                                                axis.title.x = element_text(color="black", size=14),
                                                axis.title.y=element_blank())),
                            theme = list(legend.text.align = NULL),
                            matrix=(intersection_matrix(geom=geom_point(shape='circle filled', size=3.5, stroke=0.45)) + 
                                        ylab("Database") +
                                        theme(panel.background =element_blank(),
                                            axis.line=element_blank(),
                                            axis.ticks=element_blank(),
                                            axis.title=element_text(color="black", size=14),
                                            axis.text.y = element_text(color="black", size=14),
                                            axis.text.x=element_blank())),
                            stripes=upset_stripes(geom=geom_segment(linewidth=12), colors=c('grey95', 'white')),
                            sort_sets='descending',
                            sort_intersections='descending')
}} else {{
    data_M06 <- readr::read_csv("{functional_annotation_table_file_path}")
    data_M06$PHROGS_Category <- ifelse(is.na(data_M06$PHROGS_Category), "unknown", data_M06$PHROGS_Category)
    data_M06$PFAM_Annotation <- ifelse(is.na(data_M06$PFAM_Annotation), "unknown", data_M06$PFAM_Annotation)
    # Initialize lists for each annotation method
    Pfam_list <- data.frame(Viral_gene_ID = character(0))
    PHROGS_list <- data.frame(Viral_gene_ID = character(0))
    geNomad_list <- data.frame(Viral_gene_ID = character(0))

    # Filter out rows based on PFAM_Annotation column
    Pfam_list <- data_M06 %>%
    filter(!grepl(paste(c("unknown", "Unknown", "Uncharacterized"), collapse = "|"), PFAM_Annotation)) %>%
    select(Viral_gene_ID)

    PHROGS_list <- data_M06 %>%
    filter(PHROGS_Category != "unknown" & PHROGS_Category != "Unknown") %>%
    select(Viral_gene_ID)

    geNomad_list <- data_M06 %>%
    filter(GENOMAD_Annotation != "unknown" & GENOMAD_Annotation != "Unknown") %>%
    select(Viral_gene_ID)

    # Combine all lists into a single data frame
    upset_data <- data.frame(Viral_gene_ID = data_M06$Viral_gene_ID,
                            Pfam = as.integer(data_M06$Viral_gene_ID %in% Pfam_list$Viral_gene_ID),
                            PHROGS = as.integer(data_M06$Viral_gene_ID %in% PHROGS_list$Viral_gene_ID),
                            geNomad = as.integer(data_M06$Viral_gene_ID %in% geNomad_list$Viral_gene_ID))

    p_annotation_upset <- upset(
                            upset_data, 
                            name='Group',
                            width_ratio=0.3,
                            c('Pfam', 'PHROGS', 'geNomad'),
                            queries = list(upset_query(set = 'Pfam', fill = '#CB1800'),
                                            upset_query(set = 'PHROGS', fill = '#00A87E'),
                                            upset_query(set = 'geNomad', fill = '#61BCEC')),
                            base_annotations=list('Shared genes between groups'=(intersection_size(counts=T, col = "black", 
                                                                                                    bar_number_threshold=1, width=0.8) +
                                                                                    scale_y_continuous(expand=expansion(mult=c(0, 0.05))) + 
                                                                                    theme(panel.grid=element_blank(),
                                                                                        panel.background = element_rect(fill = 'white'),
                                                                                        axis.text.x=element_blank(),
                                                                                        axis.text.y = element_text(color="black", size=14),
                                                                                        axis.title = element_text(color="black", size=14),
                                                                                        axis.title.x=element_blank(),
                                                                                        axis.line=element_line(colour='black')))),
                            set_sizes=(upset_set_size(geom=geom_bar(width=0.6, col = "black"),
                                                        position = 'right') + 
                                        geom_text(aes(label=after_stat(count)), hjust=-0.1, stat='count') +
                                        ylab("Nb of genes per group") +
                                        theme(panel.background =element_blank(),
                                                axis.line.x=element_line(colour='black'),
                                                axis.ticks.y=element_blank(),
                                                axis.text.y=element_blank(),
                                                axis.text.x = element_text(color="black", size=14),
                                                axis.title.x = element_text(color="black", size=14),
                                                axis.title.y=element_blank())),
                            theme = list(legend.text.align = NULL),
                            matrix=(intersection_matrix(geom=geom_point(shape='circle filled', size=3.5, stroke=0.45)) + 
                                        ylab("Database") +
                                        theme(panel.background =element_blank(),
                                            axis.line=element_blank(),
                                            axis.ticks=element_blank(),
                                            axis.title=element_text(color="black", size=14),
                                            axis.text.y = element_text(color="black", size=14),
                                            axis.text.x=element_blank())),
                            stripes=upset_stripes(geom=geom_segment(linewidth=12), colors=c('grey95', 'white')),
                            sort_sets='descending',
                            sort_intersections='descending')
}}

spacer <-  ggplot() +
            geom_blank(fill = "white") +  # Set the background color to white
            theme_void()

title <- ggdraw() + draw_label("Summarized plots generated by MVP\nModule 06 (Functionnal annotation) and 07 (Binning)", fontface='bold')

if ("Variable" %in% colnames(metadata)) {{
    plot_col_1 <- plot_grid(title, p_filtered_vBins, p_conservative_filtered_vBins_CheckV, p_conservative_filtered_vBins_length, p_taxa_vBins_counts,
                                ncol = 1, align = "hv", rel_heights = c(0.3, 0.6, 0.6, 1, 0.5), labels=c('','A','B', 'C', 'D'))
    plot_col_2 <- plot_grid(spacer, p_conservative_filtered_vBins_nMDS, p_annotation_upset, rel_heights = c(0.2, 0.8, 0.8),
                            ncol = 1, labels=c('','E','F'))
    combined_plots <- plot_grid(plot_col_1, plot_col_2, ncol = 2)
    print(combined_plots)
}} else {{
    plot_col_1 <- plot_grid(title, p_filtered_vBins, p_conservative_filtered_vBins_CheckV, p_conservative_filtered_vBins_length, p_taxa_vBins_counts,
                                ncol = 1, align = "hv", rel_heights = c(0.3, 0.6, 0.6, 1, 0.5), labels=c('','A','B', 'C', 'D'))
    plot_col_2 <- plot_grid(spacer, p_annotation_upset, spacer, ncol = 1, rel_heights = c(0.1, 0.6, 0.3), labels=c('', 'E',''))
    combined_plots <- plot_grid(plot_col_1, plot_col_2, rel_widths = c(0.4, 0.6), ncol = 2)
}}

ggsave("{output_folder}/Summarize_output_plots.pdf", plot = combined_plots, width = 20, height = 12)
    """.format(votu_table_file_path=votu_table_file_path, functional_annotation_table_file_path=functional_annotation_table_file_path, metadata_file_path=metadata_file_path, output_folder=output_folder)

    # Run the R code
    robjects.r(r_code)

def main(args):
    # Capture start time
    start_time = datetime.datetime.now()
    formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nStart Time: {formatted_start_time}\n") 

    metadata_file_path = os.path.join(args['metadata'])

    # Find the maximum module ran
    max_module, max_module_folder = find_max_module(args)

    # Find all summary reports
    summary_reports_dict, num_summary_reports = find_summary_reports(args, max_module_folder)

    # Get the number of summary reports in the '01_GENOMAD' directory

    print(f"\nYou have processed {num_summary_reports} samples through MVP until Module 0{max_module} ({max_module_folder}).\n")

    output_folder, output_filename = create_output_folder(args)

    # Generate the summary report
    generate_summary_report(output_filename, max_module, max_module_folder, num_summary_reports, summary_reports_dict)

    # Copy additional files based on max_module_folder

    copy_additional_files(args, max_module_folder, output_folder)

    # List of R packages to install
    install_r_packages()

    votu_table_file_name, votu_table_file_path, functional_annotation_table_file_path = find_R_tables(output_folder)

    # Run R code
    if votu_table_file_name.startswith('MVP_07_'):
        if functional_annotation_table_file_path is not None:
            create_module_06_07_figures(votu_table_file_path, functional_annotation_table_file_path, metadata_file_path, output_folder)
        else:
            create_module_07_figures(votu_table_file_path, metadata_file_path, output_folder)
    elif votu_table_file_name.startswith('MVP_05_'):
        if functional_annotation_table_file_path is not None:
            create_module_05_06_figures(votu_table_file_path, metadata_file_path, functional_annotation_table_file_path, output_folder)
        else:
            create_module_05_figures(votu_table_file_path, metadata_file_path, output_folder)
    elif votu_table_file_name.startswith('MVP_03_'):
        if functional_annotation_table_file_path is not None:
            create_module_03_06_figures(votu_table_file_path, metadata_file_path, functional_annotation_table_file_path, output_folder)
        else:
            create_module_03_figures(votu_table_file_path, metadata_file_path, output_folder)

    # Capture end time
    end_time = datetime.datetime.now()
    formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate duration
    duration = end_time - start_time

    message1 = f"\033[1mModule 100 finished: final summary report, and summary figures generated in {output_folder}!\033[0m\n"
    message2 = "\033[1mWe hope you enjoyed using MVP script, and you can now explore your data!\033[0m\n"
    message3 = "\n\033[1mPlease don't forget to cite MVP!\033[0m"
    line_of_stars = '*' * len(message1)
    print()
    print(line_of_stars)
    print(message1)
    print(f"Start Time: {formatted_start_time}") 
    print(f"End Time: {formatted_end_time}")
    print(f"Running Time: {duration.total_seconds():.2f} seconds\n")
    print(message2)
    print(message3)
    print(line_of_stars)
    print()