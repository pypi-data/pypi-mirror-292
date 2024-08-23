import regex as re

def clean_multiple_space(string):
    regex=re.compile("\s{2,}")
    search=regex.findall(string)
    for item in search:
        string=string.replace(item," ")
    return string

def my_rstrip(string,stripped):
    if isinstance(stripped,str) and string.endswith(stripped):
        string=string[:-len(stripped)]
    return string
