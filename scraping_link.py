#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from socket import gaierror
from datetime import date
import json
import os
from pathlib import Path
#-------------------
# USER input
#-------------------
username = 'agathos'
# Define keywords to match on
keywords=['actin','protein','biomaterial','light-sheet','microscopy','myosin','actomyosin','control-theory','biofilm','laser','lithography','ligand','dymer','microtubules','optical trap','thermal noise imaging','neutrophil','mechanosensing','optical tweezers','phagocytosis','pseudomonas aeruginosa','bacterial swarming','swarming motility','swarming','active matter','bacillus subtilis','sliding motility','cross-link','filament network','surface tension','cellular mechanics','self-organization','self organization','percolative','self-assembly','self assembly']
# Define journals to search
# journals=['https://advances.sciencemag.org/rss/current.xml','https://www.nature.com/subjects/biophysics/srep.rss','http://feeds.nature.com/nphoton/rss/current','http://feeds.nature.com/srep/rss/current','https://iopscience.iop.org/journal/rss/1748-3190','https://www.journals.elsevier.com/journal-of-biotechnology/rss','https://www.journals.elsevier.com/biosensors-and-bioelectronics/rss','http://feeds.nature.com/nbt/rss/current','http://feeds.feedburner.com/acs/nalefd','http://feeds.feedburner.com/acs/abseba','https://www.journals.elsevier.com/biomaterials/rss']

journals={'Science Advances':'https://advances.sciencemag.org/rss/current.xml','Nature Biophysics':'https://www.nature.com/subjects/biophysics/srep.rss','Nature Photonics':'http://feeds.nature.com/nphoton/rss/current','Nature':'http://feeds.nature.com/srep/rss/current','IOP Science':'https://iopscience.iop.org/journal/rss/1748-3190','Journal of Biotechnology':'https://www.journals.elsevier.com/journal-of-biotechnology/rss','Biosensors and Bioelectronics':'https://www.journals.elsevier.com/biosensors-and-bioelectronics/rss','Nature Biotechnology':'http://feeds.nature.com/nbt/rss/current','ACS Nanoletters':'http://feeds.feedburner.com/acs/nalefd','ACS Biomaterials':'http://feeds.feedburner.com/acs/abseba','Biomaterials':'https://www.journals.elsevier.com/biomaterials/rss'}

#----------------
# Functions
#----------------
# Scraping function
def scrape_rss(link):
    article_list=[]
    try:
        r = requests.get(link)
        soup = BeautifulSoup(r.content,features='xml')
        articles = soup.findAll('item')
        for a in articles:
            '''Extract the desired features with try to handle errors'''
            # Title
            try:
                title = a.find('title').text
            except:
                title = 'N/A'
            # Abstract
            try:
                abstract = a.find('abstract').text
            except:
                abstract = 'N/A'
            # Link
            try:
                linktmp = a.find('link').text
            except:
                linktmp = 'N/A'
            # Publish data
            try:
                published = a.find('pubDate').text
            except:
                published = 'N/A'
            article = {
                'title': title,
                'abstract': abstract,
                'link': linktmp,
                'published': published,
                }
            article_list.append(article)
        return article_list

    except Exception as e:
        print('The scraping job failed. See exception: ')
        print(e)

def remove_duplicates(list):
    fresults=[]
    ftitles=[]
    for i in list:
        if i['title'] not in ftitles:
            ftitles.append(i['title'])
            fresults.append(i)
        else:
            pass
    return fresults

def remove_oldfiles(new,old):
    fresults=[]
    # Create list of old titles
    foldtitles=[j['title'] for j in old]
    for i in new:
        if i['title'] not in foldtitles:
            fresults.append(i)
        else:
            pass
    return fresults
#------------------------
#------------------------
# Start Script
#------------------------
#------------------------

results_tot={}
for key,value in journals.items():
    article_title=key
    articles_j=scrape_rss(value)
    results=[]
    for article in articles_j:
        for i in keywords:
            if i in article['title'].lower():
               results.append(article)
    results_tot[article_title]=results

# Check if the .json file exists
writepath = r'/home/%s/Documents/python/scraping/data.json' % username
if os.path.exists(writepath):
    with open(writepath, 'r') as json_file:
        prevresults=json.load(json_file)

    # Append the previous results to the current journals
    ## Notes: Need to have a journal-by-journal function to append 
    ##        non-duplicate papers to the specifc journal.
    ##        The main difference is that these operations will need to be 
    ##        done for each journal, vs for the entire list of paper entries

# Check if the _old.json file exists
oldpath=r'/home/%s/Documents/python/scraping/data_old.json' % username
if os.path.exists(oldpath):
    with open(oldpath, 'r') as old_file:
        oldresults=json.load(old_file)

#Time to filter for duplicates & old files
if os.path.exists(oldpath):
    # for i in results_tot.values():
    #     for papers in i:
    #         fresults0=remove_duplicates(papers)
    #         fresults=remove_oldfiles(fresults0,oldresults)
    results_filtered={}
    for key,value in results_tot.items():
        prev_journals=prevresults[key]
        old_journals=oldresults[key]
        filter_journals=prev_journals+old_journals
        current_journals=value
        results_filtered=[]
        fresults_temp=remove_oldfiles(current_journals,filter_journals)
        results_filtered[key]=fresults_temp
    fresults=results_filtered


elif os.path.exists(writepath):
    # for i in results_tot.values():
    #      for papers in i:
    #          fresults=remove_duplicates(papers)
    results_filterd={}
    for key,value in results_tot.items():
        prev_journals=prevresults[key]
        current_journals=value
        results_filtered=[]
        fresults_temp=remove_oldfiles(current_journals,prev_journals)
        results_filtered[key]=fresults_temp
    fresults=results_filtered

else:
    fresults=results_tot

# Delete old .json after grabbing the previous files
if os.path.exists(writepath):
    os.remove(writepath)

### Write to .json
Path(writepath).touch()
with open(writepath, 'w') as file:
    file.write(json.dumps(fresults))
