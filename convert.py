# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 14:59:29 2018

@author: USER
"""
# Full path and name to your csv file 
csv_path="/app/data/debbie.csv" 

# Full path to your django project directory 
magnet_home="/app"

import sys,os, django
sys.path.append(magnet_home) 
os.environ['DJANGO_SETTINGS_MODULE'] = 'magnet.settings' 
django.setup()

from magnet_v030.models import Gene
import mygene,csv

def convert(file):
    mg = mygene.MyGeneInfo()
    query = []
    with open(csv_path) as csvfile:
        dataReader = csv.reader(csvfile) 
        for row in dataReader:
            if row[0] != 'Symbols':
                #print(row[0])
                query.append(row[0].upper())

    query_results = mg.querymany(query, scopes='ensemblgene', fields='symbol', species='mouse')
    #print(query_results)

    converted_symbols = []
    seen = []
    for d in query_results:
        if 'notfound' in d:
            converted_symbols.append(d['query'])
        elif d['query'] in seen:
            pass
        else:
            converted_symbols.append(d['symbol'])
            seen.append(d['query'])

    return converted_symbols


#test_list = ['ENSMUSG00000000171','abc','ENSMUSG00000000190','efg','ENSMUSG00000000244','ENSMUSG00000000303','ENSMUSG00000000440']
#test = user_convert(test_list)
#print(test[0])
#print(test[1])