# This script process the data for use in R. Many of the steps below are unnecessary, but applying all of them will ensure that the resulting csv file is properly processed for easy and efficient use in R.

# The MIT License (MIT)
#
# Copyright (c) 2014 Robert Lanfear
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


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
