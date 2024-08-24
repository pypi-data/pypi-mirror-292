### Detailed instructions for step 99 "prep_MIUViG_submission"
This script is intended for users who wish to submit individual UViGs, already processed through MVP, to a public database such as NCBI GenBank. Current recommendations are for these genomes to be accompanied by metadata following the standard MIUViG checklist (see https://doi.org/10.1038/nbt.4306, https://doi.org/10.1038/s41587-023-01844-2, and https://www.ncbi.nlm.nih.gov/genbank/structuredcomment/ for more information). This MVP module and documentation are intended to help users through the process of preparing the files required for a submission. We try to keep up-to-date with latest requirements and guidelines, however there may still be discrepancies between the files generated and the ones required by the database curators, and their recommendations should always be followed. The main steps required to generate files for submission are outlined below.

This MVP module requires users to have run *MVP at least through step 3* on the corresponding data. Because some of the information required needs to be provided and/or curated by users, the module is divided into four steps, with steps 2 and 3 being external to MVP and having to be performed by the user.

## Step 1: prepare the metadata and annotation files for the genome of interest
This step is performed with the MVP script 99_prep_MIUViG_submission as follows:
`$ python scripts/99_prep_MIUViG_submission.py -s setup_metadata -i mvp_out/ -m metadata.txt --genome genome_id_of_interest `
Two files will be created at this step. The first is a metadata file including information about how the UViG was determined to be viral, the quality of the UViG, etc. The second output is a tbl file including the gene-by-gene annotation and based on geNomad results.

## Step 2: review, curate, and complete the metadata file with sample and genome information
This step needs to be performed manually by the user, and can be done in e.g. a spreadsheet (as long as the table is exported as a tsv with the same name). Specifically, a number of fields in the metadata file generated at step 1 will be empty because they relate to information about the original sample, study, and/or additional analysis results not performed through MVP. In particular, all metadata listed as required need to be filled in. Completing the metadata can be done in any text editor or in a spreadsheet software such as Excel, in which case remember to "save as tsv" and use a "tab" delimiter.

## Step 3: register a BioSample for each genome (and BioProject if needed), and generate a corresponding tbl file
This step is not done via MVP, but can be done e.g. through the BioSample submission portal (https://submit.ncbi.nlm.nih.gov/subs/biosample/). Once all the samples and projects are registered, a submission template file should be generated via https://submit.ncbi.nlm.nih.gov/genbank/template/submission/ and downloaded (will be used later as input to the step 4 of XX_prep_MIUViG_submission script)

## Step 4: prepare the submission files
This step is performed with the MVP script XX_prep_MIUViG_submission as follows:
`$ python /scripts/99_prep_MIUViG_submission.py -s prep_submission -t template_from_biosample.sbt -i mvp_out/ -m metadata.txt -g genome_id_of_interest `
MVP will first verify that all relevant files are available and filled in, and then use table2asn to generate files ready for GenBank submission. Note that the script only verifies that a value is included for each required metadata, but does not at this time check that the value is consistent with the expected format or type of metadata.

The final files are available in XX, and will include an sqn file that can be submitted to GenBank, as well as a genbank-formatted genome file that users can use to verify that all annotation and metadata are included as expected.


### References - for more information:
Adriaenssens, E.M., Roux, S., Brister, J.R. et al. Guidelines for public database submission of uncultivated virus genome sequences for taxonomic classification. Nat Biotechnol 41, 898–902 (2023). https://doi.org/10.1038/s41587-023-01844-2

Roux, S., Adriaenssens, E., Dutilh, B. et al. Minimum Information about an Uncultivated Virus Genome (MIUViG). Nat Biotechnol 37, 29–37 (2019). https://doi.org/10.1038/nbt.4306
