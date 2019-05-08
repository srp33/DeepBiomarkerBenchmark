##install.packages(c("dplyr", "data.table", "readr"), repos="https://cloud.r-project.org")

innerFilePath = commandArgs()[7]
outerFilePath = commandArgs()[8]
outFilePath = commandArgs()[9]

suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(data.table))
suppressPackageStartupMessages(library(readr))

print("Read input file")
data <- fread(paste("zcat", innerFilePath), stringsAsFactors=TRUE, sep="\t", header=TRUE, data.table=FALSE, check.names=FALSE, showProgress=FALSE) %>% as_tibble()
data <- filter(data, Metric=="AUROC")
data <- select(data, -Metric)

print("Average across the inner iterations")
data <- ungroup(summarise(group_by(data, DatasetID, Class, OuterIteration, ClassificationAlgorithm), Value=mean(Value)))

print("Truncate parameter combos to directory names")
data$ClassifAlgoGroup <- factor(dirname(as.character(data$ClassificationAlgorithm)))

print("Pick best result for each algorithm group")
groupedData <- group_by(data, DatasetID, Class, OuterIteration, ClassifAlgoGroup)
set.seed(0)
groupedData <- filter(groupedData, rank(-Value, ties.method="random")==1) %>% ungroup() %>% select(-Value)

print("Rename column(s)")
groupedData <- dplyr::rename(groupedData, Iteration = OuterIteration)

print("Reading outer file")
outerData <- fread(paste("zcat", outerFilePath), stringsAsFactors=TRUE, sep="\t", header=TRUE, data.table=FALSE, check.names=FALSE, showProgress=FALSE) %>% as_tibble()

print("Joining inner and outer")
joinedData <- inner_join(groupedData, outerData, by=c("DatasetID", "Class", "Iteration", "ClassificationAlgorithm"))
joinedData <- select(joinedData, -ClassifAlgoGroup.y) %>% dplyr::rename(ClassifAlgoGroup=ClassifAlgoGroup.x)

print("Saving output file")
write_tsv(joinedData, outFilePath)
