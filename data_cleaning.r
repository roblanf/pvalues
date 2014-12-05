# This script process the data for use in R. Many of the steps below are unnecessary, but applying all of them will ensure that the resulting csv file is properly processed for easy and efficient use in R.

###############################################################################
# Set these variables before you run the script:

input.file.path = "p_values.csv"
output.file.path = "p_values.cleaned.csv"

###############################################################################

# Data cleaning script
d <- read.csv(input.file.path)

# PLoS ONE changed its name to PLoS One, we'll rename to just the latter
# note that the folder name stays unchanged, so you can find papers
d$journal.name[which(d$journal.name=="PLoS ONE")] <- "PLoS One"

# Pre-process numerics
d$p.value <- as.numeric(as.character(d$p.value))
d$year <- as.numeric(as.character(d$year))
d$num.authors <- as.numeric(as.character(d$num.authors))
d$num.results <- as.numeric(as.character(d$num.results))
d$num.dois <- as.numeric(as.character(d$num.dois))
d$decimal.places <- as.numeric(as.character(d$decimal.places))
d$methods.blind <- as.numeric(as.character(d$methods.blind))
d$methods.not_blind <- as.numeric(as.character(d$methods.not_blind))
d$methods.blinded <- as.numeric(as.character(d$methods.blinded))
d$methods.not_blinded <- as.numeric(as.character(d$methods.not_blinded))
d$methods.blindly <- as.numeric(as.character(d$methods.blindly))
d$methods.not_blindly <- as.numeric(as.character(d$methods.not_blindly))
d$num.methods <- as.numeric(as.character(d$num.methods))

# Pre-process factors
d$section <- as.factor(as.character(d$section))
d$first.doi <- as.factor(as.character(d$first.doi))
d$journal.name <- as.factor(as.character(d$journal.name))
d$operator <- as.factor(as.character(d$operator))
d$type.results <- as.factor(as.character(d$type.results))
d$type.methods <- as.factor(as.character(d$type.methods))
d$folder.name <- as.factor(as.character(d$folder.name))

# Pre-process booleans 
d$abstract.found <- as.logical(as.character(d$abstract.found))
d$abstract.experiment <- as.logical(as.character(d$abstract.experiment))

# Pre-proces characters
d$file.name <- as.character(d$file.name)

write.csv(d, file = ouput.file.path)