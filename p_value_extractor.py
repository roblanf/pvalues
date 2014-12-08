# This Python file uses the following encoding: utf-8

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


from bs4 import BeautifulSoup
import os
from os.path import join
import re
from random import shuffle


###############################################################################
# Set these variables before you run the script:

# input directory - all files in all subfolders will be searched
input_file_path = ""

# output file path - your results will get written to this file
output_file_path = "p_values.csv"

###############################################################################


def clarify_title(tag):
    # extract and clean up <title></title> section from any tag
    # so e.g. results/discussion, '3. Results and Discussion', 'iii. Results \n& Discussion '
    # all become "results and discussion"
    try:
        title = tag.find('title').text.lower()
        title = title.encode('ascii', errors = "ignore")
        title = title.replace('\n', ' ').replace('\r', ' ') # remove line breaks
        # remove leading and trailing whitespace, numbers, full stops, and roman numerals
        title = title.strip()
        title = title.strip('0123456789ivx.:() ')
        title = title.strip()
        title = title.replace("&", "and")
        title = title.replace("/", "and")
        title = title.replace("|", "and")

    except Exception, e:
        title = ""

    return(title)

def tag_checker(tag, possible_titles, type=1):
    # a function to check a given tag to see if it contains any of
    # the words in possible_titles
    # type==1 is strict and checks only the <sec> attributes for the poss_title
    # see: http://dtd.nlm.nih.gov/publishing/tag-library/3.0/
    # type==2 is more relaxed, and checks the text of the <sec> tag

    title = clarify_title(tag)


    for poss_title in possible_titles:

        if type==1:
            try:
                if tag.attrs.values().count(poss_title)>0:
                    return(True)
            except Exception, e:
                pass

        # if it's not nicely listed in the attrs
        # we can look at the top section title
        if type==2:
            if len(title)>0 and title==poss_title:
                return(True)

    # # this is useful for diagnosing things to include in the possible titles...
    # # e.g. change 'results' to 'methods', or any other section you're looking for
    if title.count("results")>0 and type==2 and possible_titles[1]=="results":
        #print title

    # got to here, couldn't find the search words in the tag

    return(False)

def is_results(tag, type=1):
    # list of possible titles compiled by scouring all section titles that contain the word 'results'
    # from the May 2013 pubmed open access subset
    # ordered in roughly decreasing frequency
    possible_titles = ['results', 'results and discussion', 'methods and results', 'results and discussions',
                        'results, discussion and conclusions', 'discussion and results',
                        'study results', 'results and conclusions', 'results and conclusion',
                        'experimental results', 'observations and results',
                        'results and observations', 'results and observation',
                        'observations, results and discussion', 'empirical results', 'materials and results',
                        'experimental procedures and results', 'research results', 'analysis and results',
                        'results and analysis', 'methodsandresults', 'resultsanddiscussion', 'resultsandconclusions',
                        'method and results']
    return(tag_checker(tag, possible_titles, type))

def is_methods(tag, type=1):
    search_words = ['methods', 'materials and methods', "material and methods"]
    return(tag_checker(tag, search_words, type))

def is_blind(text):
    # A function to search for the word 'blind' in text
    reg1 = re.compile(ur"\W[Bb]lind\W", re.UNICODE)
    blind = len(reg1.findall(text))

    reg1 = re.compile(ur"\W[Nn]ot[\s]blind\W", re.UNICODE)
    not_blind = len(reg1.findall(text))

    reg1 = re.compile(ur"\W[Bb]linded\W", re.UNICODE)
    blinded = len(reg1.findall(text))

    reg1 = re.compile(ur"\W[Nn]ot[\s]blinded\W", re.UNICODE)
    not_blinded = len(reg1.findall(text))

    reg1 = re.compile(ur"\W[Bb]lindly\W", re.UNICODE)
    blindly = len(reg1.findall(text))

    reg1 = re.compile(ur"\W[Nn]ot[\s]blindly\W", re.UNICODE)
    not_blindly = len(reg1.findall(text))

    return(blind, not_blind, blinded, not_blinded, blindly, not_blindly)

def has_experiment(text):
    # A function to search for the words
    # 'experiment', 'experimental', 'experimentally' in text
    reg1 = re.compile(ur"\W[Ee]xperiment\W", re.UNICODE)
    reg2 = re.compile(ur"\W[Ee]xperimental\W", re.UNICODE)
    reg3 = re.compile(ur"\W[Ee]xperimentally\W", re.UNICODE)

    matches = reg1.findall(text) + reg2.findall(text) + reg3.findall(text)
    if len(matches)>0:
        found = True
    else:
        found = False
    return(found)


def extract_p_values(text, label):
    # A function to extract p values from a string of text
    # [^a-zA-Z0-9*_] is any non-whitespace and non-symbol (*#†)
    # the [0]? matches zero or one '0', some p values are reported as "p < .001"
    regex = re.compile(ur"[^a-zA-Z0-9*#†_][Pp][\s]*[=<>≤≥][\s]*[01]?[.][\d]+", re.UNICODE)
    matches = regex.findall(text)
    pvals = []
    # strip the first character, then the 'p' or 'P'
    for i, match in enumerate(matches):
        match = "".join(match.split()) # remove all whitespace

        # now extract just the 'p=' part...
        regex = re.compile(ur"[Pp][\s]*[=<>≤≥][\s]*[01]?[.][\d]+", re.UNICODE)
        match = regex.findall(match)[0]
        operator = match[1]
        val = match[2:]
        decimal_places = len(val.split('.')[1])
        val = float(val)
        if val <= 1.0:
          pval = [operator, val, decimal_places, label]
          pvals.append(pval)

    return(pvals)

def extract_first_doi(soup):
    # This could be a lot more efficient, but it works
    # run through all article-id tags return DOI if you find it
    for tag in soup.find_all('article-id'):
         if tag.attrs.values().count('doi')>0:
            return(tag.text.replace("\n", "")) # some DOIs have newlines!

    # if you get to here, you didn't find a DOI
    return("NA") # use NA because we post-process in R

def extract_journal(soup):
    # This could be a lot more efficient
    # run through all journal-id tags and return journal title
    for tag in soup.find_all('journal-id'):
         if tag.attrs.values().count('nlm-ta')>0:
            journal = tag.text.replace("\n", "")
            journal = "".join(['"', journal, '"'])
            return(journal)

    # if you get to here, you didn't find a title
    return("NA") # use NA because we post-process in R

def get_num_authors(soup):

    total = 0
    for tag in soup.find_all('contrib'):
         if tag.attrs.values().count('author')>0:
            total = total + 1
    return(total)


def get_num_dois(soup):
    # some of the .nxmls contain huge collections of articles
    # one way to find these is to find all the DOI tags in
    # an article and count them. >1 indicates trouble.
    # example file is:
    # J_Int_AIDS_Soc_2012_Oct_22_15(Suppl_3)_10_7448_IAS_15_5_18440.nxml
    dois = set()

    for tag in soup.find_all('article-id'):
         if tag.attrs.values().count('doi')>0:
            dois.add(tag.text)

    return(len(dois))


def get_year(soup):
    # just take the year of the first pub-date tag
    year = "NA"
    tags = soup.find_all('pub-date')
    try:
        year = tags[0].find_all('year')[0].text
    except:
        pass

    year = year.replace("\n", "")

    # the return strips newlines, which can be an issue
    return(year)

def extract_abstract(soup):
    # function to get the abstract. Recorded in <abstract> section
    try:
        # some papers have >1 abstract, since one is a 'precis'
        abstracts = soup.find_all("abstract")
        abstract = max(abstracts, key=len).get_text()
        abstract = clarify_text(abstract)
        abstract_found = True
    except Exception, e:
        abstract = ""
        abstract_found = False

    return(abstract, abstract_found)

def extract_section(soup, extractor_function):
    section_text = ""
    type = "None"

    # we try two things - the proper tag, or a header we want
    section_text = []
    for tag in soup.find_all('sec'):
        if extractor_function(tag, type=1):
            section_text = [tag.get_text()]
            type = 'PubMed DTD'
            break # we found a properly formatted section
        if extractor_function(tag, type=2):
            section_text.append(tag.get_text())
            type = 'Section title'

    n = len(section_text)

    # if we found >1 title matching e.g. 'Results', we keep the longest one
    # N.B. this will only ever occur if type=='section title'
    if section_text:
        section_text = max(section_text, key=len)
        section_text = clarify_text(section_text)
    else:
        section_text = ""

    return(section_text, n, type)

def clarify_text(text):
    # remove unwanted elements from any block of text

    text = text.replace("\n", " ")
    text = text.replace("\r", " ")

    return(text)

def clarify_soup(soup):
    # remove all unwanted bits from the soup

    # Remove subtext, so we can mine e.g. "P <sub>I vs D</sub>&#x0003c;0.0001"
    trash = [s.extract() for s in soup('sub')]

    # remove table and figure captions
    trash = [s.extract() for s in soup('table')]
    trash = [s.extract() for s in soup('caption')]
    trash = [s.extract() for s in soup('table-wrap')]
    trash = [s.extract() for s in soup('table-wrap-foot')]

    return(soup)


def process_paper(file_path):
    # put everything together to process a single nxml file
    p_values = []

    soup = BeautifulSoup(open(file_path), 'xml')
    soup = clarify_soup(soup)

    # get p values from abstract
    # p_values is a list of lists of [value, operator, label, section]
    abstract, abstract_found = extract_abstract(soup)
    if abstract_found==True:
        p_values = p_values + extract_p_values(abstract, 'abstract')

    trash = [s.extract() for s in soup('abstract')]

    # get p values from results
    results, num_results, type_results = extract_section(soup, is_results)
    if num_results > 0:
        p_values = p_values + extract_p_values(results, 'results')

    if len(p_values)==0:
        p_values.append(["NA", "NA", "NA", "NA"]) # to record all papers at least once


    # extract the text of the methods section
    methods, num_methods, type_methods = extract_section(soup, is_methods)

    blind, not_blind, blinded, not_blinded, blindly, not_blindly = is_blind(methods)
    experiment_abstract = has_experiment(abstract)
    doi = extract_first_doi(soup)
    journal = extract_journal(soup)
    num_authors = get_num_authors(soup)
    num_dois = get_num_dois(soup)
    year = get_year(soup)

    row_end = [str(doi), str(num_dois), str(journal), str(abstract_found), str(experiment_abstract), str(blind), str(not_blind), str(blinded), str(not_blinded), str(blindly), str(not_blindly), str(num_methods), str(type_methods), str(num_results), str(type_results), str(num_authors), str(year)]

    rows = []

    # now we make one row per p value (or just one row with 'NA's for p values if there were none)
    for p in p_values:
        row = [str(p[1])] + [p[0]] + [str(p[2])] + [str(p[3])] + row_end
        rows.append(row)

    return(rows)


def get_all_papers(head_directory_path):
    # a function to walk through files recursively and yield *.nxml files
    for root, dirs, files in os.walk(head_directory_path):
        shuffle(dirs) # useful for development - so you don't always optimse for journals starting with 'A'
        dirs.sort(reverse=True) # useful for development - so you don't always optimse for journals starting with 'A'
        for curfile in files:
            if curfile.endswith(".nxml"):
                yield join(root, curfile)



# A hard-coded script to run the above functions.
header = ["p.value", "operator", "decimal.places", "section", "first.doi", "num.dois", "journal.name", "abstract.found", "abstract.experiment", "methods.blind", "methods.not_blind", "methods.blinded", "methods.not_blinded", "methods.blindly", "methods.not_blindly", "num.methods", "type.methods", "num.results", "type.results", "num.authors", "year", "file.name", "folder.name"]

outfile = open(output_file_path, 'w')
header = ",".join(header)
header = header.rstrip(",")
outfile.write(header)
outfile.write("\n")

paper_num = 1

for paper_path in get_all_papers(input_file_path):

    result = process_paper(paper_path)
    paper_name = os.path.basename(paper_path)

    # perhaps a useful alternative to extracting the journal from the .nxml file
    folder_name = os.path.basename(os.path.split(paper_path)[0])
    folder_name = "".join(['"', folder_name, '"'])

    # 'result' is a list of lists, where each sub-list represents a p-value
    # or a filler row which designates that no p-values were found
    for r in result:
        w = r + [paper_name] + [folder_name]
        w = ",".join(w)
        w = w.rstrip(",")
        w = "".join([w, "\n"])
        outfile.write(w.encode('utf-8'))

    if paper_num % 100 == 0:
        print "done", paper_num, "papers"
    paper_num = paper_num + 1

outfile.close()
