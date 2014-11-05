# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # Ghalib Concordance Generator

# <markdowncell>

# ## Description
# 
# This notebook contains code to generator a concordance for the muravvaj divaan of ghalib.
# 
# Verses are taken from "input/verses.csv"
# 
# The current task is to identify the proper lemma of the tokens, e.g. singular instead of plural,
# verb infinitive instead of verb root, etc. This can partially be done computationally.
# 
# Lemma that remain to be checked are in "output/tocheck.csv" The first column, if marked as 'x',
# means that entry is okay. Checked lemma can then be entered into "input/okay.csv" using the
# functions 
# 

# <headingcell level=2>

# Variables

# <codecell>

verses = {} # dictionary of verses, e.g. 001.01.0='naqsh faryaadii..'
tokens = {} # dictionary of tokens where key is verses+.xx, e.g. 001.01.0.01 = 'naqsh'
unique_tokens = {} # dictionary of tokens where value is their count
lemmas = {} # dictionary of tokens where value is a list of their lemmas
unique_lemmas = [] # dictionary of unique lemmas
okay_lemmas = {} # dictionary of unique tokens and lists of lemma, e.

# <markdowncell>

# ##Functions

# <codecell>

import re

def load_verses(inputfile='input/verses.csv'):
    '''
    Loads verses from CSV data file
    inputfile: name of csv file
    returns: verses where verses['ggg.vv.l']=token; where ggg=ghazal #; vv=verse number;l=line number
    '''

    import csv
    verses = {}
    with open(inputfile,'r') as csvfile:
        versereader = csv.reader(csvfile)
        for row in versereader:
            (verse_id, input_string, real_scan) = row # 
            if not 'x' in verse_id: # skip ones with x (not in muravvaj divan)
                verses[verse_id] = input_string.strip()
    return verses

def get_okay_lemmas(inputfile='input/okay.csv'):
    '''
    Loads checked lemmas from CSV data file
    inputfile: name of csv file
    returns: checked_lemmas where checked_lemmas['token'] = [lemmas]
    '''

    import csv
    okay_lemmas = {}
    with open(inputfile,'r') as csvfile:
        versereader = csv.reader(csvfile)
        for row in versereader:
            (status, unique_token, lemmas) = row
            assert status in ['','x']
            if status=='x':
                okay_lemmas[unique_token]=lemmas.split('|')
    return okay_lemmas


def get_tokens(verses):
    '''
    Identifies tokens in verses
    verses: verses
    returns: tokens, where tokens['ggg.vv.l.tt']=token {tt = token # on line starting  at zero}
    '''
    tokens = {}
    for k in verses.keys():
        v_tokens = verses[k].split(' ')
        for id,t in enumerate(v_tokens):
            token_id = k+'.'+str(id).zfill(2)
            tokens[token_id] = t
    return tokens

def locate_token(token):
    '''
    Finds locations of token
    token: string 
    Input: token (string)
    returns: a list of locations, e.g. [001.01.0.01]
    '''
    assert tokens
    return [k  for k,v in tokens.iteritems() if v==token]

def match_tokens(match_string):
    '''
    Finds tokens matching a pattern (from start)
    match_string: regular expression string (assumes ^,e.g. 'naq')
    returns: a list of tokens,e.g. ['naqsh']
    '''
    import re
    assert unique_tokens
    return [k  for k in unique_tokens.keys() if re.match(match_string,k)]

def search_tokens(match_string):
    '''
    Searches for tokens matching a pattern (anywhere in it)
    match_string: regular expression of string
    Input: regular expression string (e.g. 'aqsh'
    returns: a list of tokens, e.g. ['naqsh']
    '''
    import re
    assert unique_tokens
    return [k  for k in unique_tokens.keys() if re.search(match_string,k)]

def get_unique_tokens(tokens):
    '''
    Finds unique tokens
    tokens: a dictionary of tokens at locations, e.g. tokens['001.01.0.00']='naqsh'
    returns: a dictionary of unique tokens and their count, unique_tokens['token']=1
    '''
    unique = {}
#    print type(tokens)
    for k,t in tokens.iteritems():

        if not t in unique: 
            unique[t]=0
            
        unique[t]+=1
    return unique


def get_lemmas(unique_tokens):
    '''
    Generate lemmas of tokens
    unique_tokens: dictionary of unique tokens
    returns: lemmas[original_token]=['lemma1','lemma2']
    '''
    lemmas = {}

    for t in unique_tokens.keys():
        lemma = t

        if re.search("[-']haa$",t): 
            lemma = t[:-4] # remove Persian plural ['-]haa ending
        if re.search("-e$",t):
            lemma = t[:-2] # remove izaafat ending '-e'
#            print lemma
        t_lemmas = [lemma]
        if re.search('-o-',lemma):
            nouns = lemma.split('-o-')
            t_lemmas = t_lemmas + nouns
            
        lemmas[t]=t_lemmas
    return lemmas

def get_unique_lemmas(lemmas):
    '''
    Generates unique lemma forms
    lemmas: dictionary keyed by tokens containing lists of lemma, e.g. lemmas['rang-o-buu']=['rang','buu','rang-o-buu']
    returns: unique_lemmas as unique_lemmas['lemma']=count
    '''
    unique_lemmas = []
    for t,t_lemmas in lemmas.iteritems():
        for lemma in t_lemmas:
            if not lemma in unique_lemmas:
                unique_lemmas.append(lemma)
#            else:
#                unique_lemmas[lemma].append(t)
    return unique_lemmas


# <markdowncell>

# ## Set Variables

# <codecell>

verses = load_verses()
tokens = get_tokens(verses)
unique_tokens = get_unique_tokens(tokens)
lemmas = get_lemmas(unique_tokens)
unique_lemmas = get_unique_lemmas(lemmas)
okay_lemmas = get_okay_lemmas()

print "Currently checked ",len(okay_lemmas)," of ",len(unique_lemmas)

# <markdowncell>

# ## Update Files

# <codecell>

def update_to_check():
    '''
    Writes unique tokens not contained in okay_lemmas to output/tocheck.csv
    '''
    with open('output/tocheck.csv','w') as f:
        for t in sorted(unique_tokens.keys()):
            if not t in okay_lemmas: # only add unchecked ones
                line  = "," # good or bad
                line += t+"," #token
                line += '|'.join(lemmas[t]) # possible lemma of token
                line += "\n" 
                f.write(line)

def update_okay(inputfile='output/tocheck.csv'):
    '''
    Loads lemmas noted as correct from inputfile into okay_lemmas
    '''
    lemmas_to_add = get_okay_lemmas(inputfile=inputfile)
    for k,v in lemmas_to_add.iteritems():
        if k in okay_lemmas:
            print "WARNING: ",k," found in okay_lemmas. Will override."
        okay_lemmas[k] = v
    
def write_okay(outputfile='input/okay.csv'):
    '''
    Writes okay_lemmas to outputfile, as status,token,lemma1|lemma2|lemma3
    '''
    with open(outputfile,'w') as f:
        for t in sorted(okay_lemmas.keys()):
            line  = "x," # good or bad
            line += t+"," #token
            line += '|'.join(okay_lemmas[t])
            line += "\n" 
            f.write(line)

def update_files():
    '''
    Loads lemmas noted as correct from tocheck.csv, 
    Writes okay_lemmas as input/okay.csv
    Regenerates output/tocheck.csv
    '''
    update_okay() 
    write_okay()
    update_to_check()
                    

# <codecell>

update_files()

