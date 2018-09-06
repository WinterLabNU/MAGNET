# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 15:01:45 2018

@author: USER
"""

# Full path and name to your csv file 
csv_path="/app/data/Gautier2012.csv" 

# Full path to your django project directory 
magnet_home="/app"

 
import sys,os, django
sys.path.append(magnet_home) 
os.environ['DJANGO_SETTINGS_MODULE'] = 'magnet.settings' 
django.setup()

from magnet_v030.models import Gene, Dataset, Cluster, Annotation, Alias
from django.db import transaction
from convert import convert

import csv

@transaction.atomic
def import_csv_symbol(csv_path):
    with open(csv_path) as csvfile:
        dataset_name = os.path.splitext(os.path.basename(csvfile.name))[0]
        dataset = Dataset(dataset_name = dataset_name)
        dataset.save()
        
        missed_genes = []
        dataReader = csv.reader(csvfile) 
        for row in dataReader:
            if row[0] != 'Symbols':
                print(row[0])
                # create gene entries if they do not exist
                if Gene.objects.filter(gene_symbol = row[0].upper()).exists():
                    gene = Gene.objects.get(gene_symbol=row[0].upper())
                elif Alias.objects.filter(alias_name=row[0].upper()).exists():
                    gene = Alias.objects.filter(alias_name=row[0].upper())[:1].get().gene
                else:
                    missed_genes.append(row[0])
                    gene = Gene(gene_symbol=row[0].upper())
                    gene.save()
                
                # create clusters
                if not dataset.cluster_set.filter(cluster_number=row[1]).exists():
                    cluster = dataset.cluster_set.create(cluster_number = row[1])
                else:
                    cluster = dataset.cluster_set.get(cluster_number = row[1])
                
                # create annotation
                annotation = Annotation(gene = gene, cluster = cluster)
                annotation.save()
    print(missed_genes)
    print(len(missed_genes))
    return "Operations completed!"

@transaction.atomic
def import_csv_ensembl(csv_path):
    
    # convert to gene symbols
    gene_symbols = convert(csv_path)
    
    with open(csv_path) as csvfile:
        dataset_name = os.path.splitext(os.path.basename(csvfile.name))[0]
        dataset = Dataset(dataset_name = dataset_name)
        dataset.save()
        
        missed_genes = []
        dataReader = csv.reader(csvfile)
        
        cluster_number = [row[1] for row in dataReader if row[0] != 'Symbols']
        
    for g, c in zip(gene_symbols, cluster_number):
        #print(g + ' ' + c)
  
        # create gene entries if they do not exist
        if Gene.objects.filter(gene_symbol = g.upper()).exists():
            gene = Gene.objects.get(gene_symbol=g.upper())
        elif Alias.objects.filter(alias_name=g.upper()).exists():
            gene = Alias.objects.filter(alias_name=g.upper())[:1].get().gene
        else:
            missed_genes.append(g)
            gene = Gene(gene_symbol=g.upper())
            gene.save()
                
        # create clusters
        if not dataset.cluster_set.filter(cluster_number=c).exists():
            cluster = dataset.cluster_set.create(cluster_number = c)
        else:
            cluster = dataset.cluster_set.get(cluster_number = c)
                
            # create annotation
            annotation = Annotation(gene = gene, cluster = cluster)
            annotation.save()
            
    print(len(gene_symbols))
    print(len(cluster_number))
    
    print(missed_genes)
    print(len(missed_genes))
    
    return "Operations completed!"
    
    
import_csv_symbol(csv_path)