README
------

This is a script to extract p values from open access articles.

Quickstart
----------
To generate the data and run the scripts yourself on the latest PubMed OA subset:

1. Download and unzip these four files into a single folder:
    ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/articles.A-B.tar.gz
    ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/articles.C-H.tar.gz
    ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/articles.I-N.tar.gz
    ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/articles.O-Z.tar.gz

2. Change the input_file_path at the top of the p_value_extractor.py script to point to the folder you put the open access files in

3. Run the p_value_extractor.py script (python 2.7.x will work) (~24 hours run time)*

4. Change the file paths in the data_cleaning.r script

5. Optionally: Run data_cleaning.r to pre-process and clean the data for use in R

6. Optionally: run the lines of R code below to try and exclude non-research papers

*You will need to install the bs4 dependency at the top of the script; you will also need to know how to run python scripts. Figuring this out is easy with google.

Tips
----
* The output CSV files are put together with R in mind, so they are large and somewhat unwieldy.
* Be careful about the limitations of the script. It may not do what you want, or what you think it does. See particularly the known limitations, below.
* The python script mines every single .nxml file in the PubMed OA dataset. This is not what most people want. Most people want p values from research articles only. It's hard to be 100% certain that you can just get research articles, but here are a few lines of R code which you can run **after running the data_cleaning.r script** that will clean things up a great deal (explanations in comments):

''''

    # set this file path to the output of the python script
    filepath <- "p_values.csv"

    # open up the data
    d <- read.csv(filepath)

    # only keep the papers with a single DOI, since some legitimately have 0 or >1
    d <- d[which(d$num.dois==1),]

    # only keep papers where we have >0 results sections (reviews and commentaries often have 0 results sections)
    d <- d[which(d$num.results > 0),]

    # only keep papers with at least one author (some non-research papers legitimately have zero)
    d <- d[which(d$num.authors>0),]

    # some journals publish large 'supplements' that contain conference many short conference abstracts (with results sections) in one file. Remove these
    d <- d[-c(grep("(Suppl)", d$file.name)),]

''''

p_value_extractor.py
--------------------

Python script to extract p values from PubMed OA subset .nxml files. This script was developed iteratively - each time the script was run, 20 papers with at least one p value were manually selected and checked by hand. All cases in which the script could be improved were recorded, and as long as at least one improvement was made, the script was re-run. When no further improvements could be made like this, the script was run one more time. The information on accuracy given below was then put together by randomly selecting 100 papers for which the script had found p-values, and then extracting p-values from those papers by hand.

The script uses BeautifulSoup 4 to mine p values (p=, p<, p>, p<=, p>=) from the abstract and results sections of .nxml files. The script itself provides the best summary of what it does, but the basic aim is to find all text that starts with 'p=', 'p<', or 'p>', etc, followed by a number between zero and one, and parse the number and the operator.

Known limitations:

1. Figure captions are excluded

2. Tables and table captions are excluded

3. Statements like "The significance level was P < 0.05 in all cases." will record a single p value - we cannot automatically parse case numbers.

4. There are occasional instances of false positives, e.g. from phrases such as "Statistical significance was taken as p<0.05".

5. There may be occasional (though I have not seen any) cases where a parameter 'P' of a model is reported as e.g. P=0.035. The script will assume this is a p value and extract it.

6. The script will miss non-standard reporting, e.g. "p=ns" for non-significant p values.

Accuracy:

In general, you should check the accuracy yourself, by analysing at least 100 papers by hand for whatever purpose you are using the script for. I cannot guarantee its accuracy.

For an earlier version of the script, I checked the accuracy of by manually extracting p values (excluding those in tables, figures, and legends) from the abstracts and results sections of 100 papers. Of the 744 p-values I extracted, I found  15 cases in which the script failed to extract a reported p value (2%). Of these, seven were due to the script being unable to parse scientific notation, four were due to p values being reported in ranges or lists (e.g. “p = 0.02 – 0.04”), three were due to typographical errors in the published manuscript (e.g. “p = <0.00006”), and one was due to a p value of exactly 1.0 (this error does not occur in the current version of the script). I found two false positives, both of which involved the script recording p values from papers that describe alpha values in terms of a p value threshold (e.g. ‘Statistical significance was taken as P < 0.05’). Please note that this method of checking the accuracy may not be appropriate for you. You should be careful to do an appropriate check yourself before using any data you produce.

Please pay careful attention to these types of errors if you use this script to generate data for any of your own analyses. If you have suggested improvements to the script please raise an issue on GitHub rather than emailing me directly, or feel free copy the repo, make them yourself, and submit a pull request.

Output file
-----------

The script will generate an output file with the following columns:

* p.value: p value extracted from the paper. "NA" for files with no p values

* operator: '<', '>', '=', '≤' and '≥'. (Note that those last two characters do not always display correctly on all operating systems, they are <= (less than or equal to) and >= (greater than or equal to) respectively.

* decimal.places: the number of decimal places to which the p value was reported

* section: section in which the p value was found. 'results', 'abstract', or 'NA' for papers with no p values found

* first.doi: the first DOI in the paper, 'NA' for papers where the script could not find a DOI.

* num.dois: the number of DOIs reported in the paper (useful for excluding non-research papers - some .nxml files contain many documents so have many dois)

* journal.name: name of the journal, extracted from the .nxml file itself. In most cases this should be identical to the folder.name (see below)

* abstract.found: 'True' or 'False' depending on whether an 'abstract'  section was found in the xml tags

* abstract.experiment: 'True' or 'False'. 'True' if the words experiment, experimental, or experimentally appear in the abstract (with or without capitalisation). 'False' otherwise.

* methods.blind: 'True' if the 'methods' section contains the word 'blind' (capitalistaion ignored). 'False' otherwise.

* methods.not_blind: 'True' if the 'methods' section contains the phrase 'not blind' (capitalistaion ignored). 'False' otherwise.

* methods.blinded: 'True' if the 'methods' section contains the word 'blinded' (capitalistaion ignored). 'False' otherwise.

* methods.not_blinded: 'True' if the 'methods' section contains the phrase 'not blinded' (capitalistaion ignored). 'False' otherwise.

* methods.blindly: 'True' if the 'methods' section contains the word 'blindly' (capitalistaion ignored). 'False' otherwise.

* methods.not_blindly: 'True' if the 'methods' section contains the phrase 'not blindly' (capitalistaion ignored). 'False' otherwise.

* num.methods: number of methods sections found. Occasionally the script finds > 1 methods section, particularly in papers which did not use the appropriate section tags. When >1 methods section is found, the script keeps only the longest section.

* type.methods: 'PubMed DTD' or 'Section title'. The former is most reliable, and occurs only when the .nxml file has a section tagged as 'methods' according to PubMed's xml style guidelines. The latter occurs when there were no appropriately tagged sections, and instead finds the longest section that matches one of many possible section headings for methods sections (see the script for the full list).

* num.results: number of results sections found. Occasionally the script finds > 1 results section, particularly in papers which did not use the appropriate section tags. When >1 results section is found, the script keeps only the longest section.

* type.results: 'PubMed DTD' or 'Section title'. The former is most reliable, and occurs only when the .nxml file has a section tagged as 'results' according to PubMed's xml style guidelines. The latter occurs when there were no appropriately tagged sections, and instead finds the longest section that matches one of many possible section headings for results sections (see the script for the full list).

* num.authors: Number of authors, extracted from the .nxml file.

* year: Year of publication, extracted from the .nxml file.

* file.name: .nxml file name. Combined with the folder.name column, this allows you to double check any of the .nxml files by hand, and also crossreference it with the published version using the first.doi column.

* folder.name: folder in which the .nxml file is contained. Usually the same as journal.name, but kept because in occasionally we want to clean up journal.name (e.g. PLOS ONE has two names, so we change the journal name but not the folder name), and also to allow one to easily trace back to original files for checking the script.

data_cleaning.r
---------------

Takes the csv file from the Python script as input, and produces a cleaned version appropriate for analysis in R.

Filepaths will need to be fixed at the top of the script.

In brief, the script:

1. Changes "PLoS ONE" in journal.name to "PLoS One", because both names are used in the database, but refer to a single journal

2. Sets all variables to appropriate types for R. E.g. changes the text 'True' to the logical variable 'TRUE' recognised by R.
