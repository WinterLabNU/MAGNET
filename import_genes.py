# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 11:19:15 2018

@author: USER
"""
# Full path and name to your gene file 
path="/app/mgi_symbols.txt" 

# Full path to your django project directory 
magnet_home="/app"
 
import sys,os, django
sys.path.append(magnet_home) 
os.environ['DJANGO_SETTINGS_MODULE'] = 'magnet.settings' 
django.setup()

from magnet_v030.models import Gene, Alias
from django.db import transaction
import csv

@transaction.atomic
def import_gene(path):
    with open(path) as f:
        next(f)
        reader=csv.reader(f,delimiter="\t")
        
        for symbol, alias in reader:
            # create gene entries if they do not exist
            if not Gene.objects.filter(gene_symbol=symbol.upper()).exists():
                gene = Gene(gene_symbol=symbol.upper())
                gene.save()
            else:
                gene = Gene.objects.get(gene_symbol=symbol.upper())
                    
            print(symbol)
            # split aliases
            aliases = alias.split("|")
                
            for e in aliases:
                if not gene.alias_set.filter(alias_name=e.upper()).exists() and e != "-":
                    alias = gene.alias_set.create(alias_name = e.upper())
                    print(e)
                
    return "Operations completed!"

import_gene(path)