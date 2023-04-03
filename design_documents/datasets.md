# Brief description of datasets for the QuicK-mer2 extension

1. Testing data: A sample QuicK-mer2 output bed file to test on (Sample DM09, belonging to GMKF Charge Data, private patient data not linked here)
The output bedfile contains four columns: chromosome, start coordinate, end coordinate, copy number
Validation: already ran through QuicK-mer2, and test file was originally sampled in a collaborative project (https://pubmed.ncbi.nlm.nih.gov/29300383/), but data is not public

2. Required comparison data: All samples involved in the 1000 Genomes Project, processed through QuicK-mer2
Each bed file will be processed into a final numpy table, where row = sample and column = window coordinates (pre-decided based on reference genome, hg38), and each entry is a sample's copy number at that window
This table will be created during this process and provided for future use

Samples for the 1000 Genomes Project can be found here: http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000_genomes_project/, whose parent host is the International Genome Sample Resource (IGSR), the host of the 1000 Genomes Project (https://www.internationalgenome.org/data/). 

3. Real Dataset for answering a biological question using QuicK-mer2
This tutorial will extend from the original tutorial that downloads sample NA12878, another sample from the 1000 Genomes project, that is being used for continuity. This tutorial can be tested using any patient data; we recommend those that are publicly available through the Gabriella Miller Kids First Data Resource Center to determine rare variants in the target patient population. You must first run the QuicK-mer2 tutorial that uses sample NA12878, or use the bed file made in the https://github.com/KiddLab/QuicK-mer2/tree/master/tutorial-sample-results folder. This is a good sample because it is no different from your standard file. However, we recommend that if you have access, to instead test this pipeline on patient disease data, many of which is not publicly available due to privacy concerns. Thus, we remain using sample NA12878. We seek to answer the question on whether or not NA12878 has rare duplications or deletions, which can lead to downstream analysis of genes, enhancers, or present regulatory regions (not included here). We expect, by pure chance, to find at least one rare duplication or deletion. However, because NA12878 has no pre-eminent disease we are aware of, we don't expect great variation from the 1000 Genomes table. 