# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 15:38:53 2018

@author: USER
"""

# Create your tasks here
from __future__ import absolute_import, unicode_literals

from django.db import connection
from django.db.models import Q
import mygene
import json
import scipy.stats as sp
import statsmodels.sandbox.stats.multicomp as mt
from celery import task
from celery_progress.backend import ProgressRecorder

from .models import Gene, Dataset, Cluster, Annotation, Alias
from .result_object import result_object
from . import helper

progress_recorder = None
progress = None
total = None

@task(bind=True)
def task_wrapper(self, user_data):
    
    global progress_recorder, progress, total
    progress_recorder = ProgressRecorder(self)
    progress = 0
    
    user_genes, user_background, user_choices, background_calc = user_data
    
    total = len(user_genes)*3 + 2
    progress_recorder.set_progress(0, total)
    
    user_background_converted = helper.user_convert(user_background)
    progress_recorder.set_progress(1, total)
    
    hg_output = hypergeom_wrapper(user_genes, user_background_converted[0], 
                                      user_choices, background_calc,
                                      total,progress_recorder)
    
    results = hg_output['results']
    missed_genes =  hg_output['missed_genes']
    missed_background = hg_output['missed_background']+ user_background_converted[1] 
    matched_num = [hg_output['matched_gene_num'],hg_output['matched_bg_num']]
    
    # get total number of genes the user submitted
    user_gene_num = list(user_genes.values()) 
    user_gene_num = len([e for sublist in user_gene_num for e in sublist])
    
    orig_num = [user_gene_num,len(user_background)]
    
     ## filter for significant entries
    sig_results =[r for r in results if r.pval <= 0.05]
    
    ## split the entries by dataset and user_cluster
    dataset_dict = {}
    for d in Dataset.objects.filter(pk__in=user_choices):
        dataset_list = [r for r in results if r.dataset_name==str(d)]
        for user_cluster in user_genes:
            user_cluster_list = [r for r in dataset_list if r.user_cluster==user_cluster]
            
            if d.id in dataset_dict:
                dataset_dict[d.id].append((user_cluster, user_cluster_list)) 
            else:
                dataset_dict[d.id] = [(user_cluster, user_cluster_list)]
    
    # convert significant result objects into dictionary for session variables
    session_dict = {}    
    for e in sig_results:
        session_dict[(e.dataset_name,e.cluster_description)] = [e.pval, e.adjusted_pval, e.N, e.B, e.n, e.b]
    
    session_dict = helper.convert_keys_toStr(session_dict)
    session_dict = json.dumps(session_dict)
    
    progress_recorder.set_progress(total, total)
    
    context = {'sig_results': sig_results, 'dataset_dict': dataset_dict,
               'missed_genes': missed_genes, 'missed_background': missed_background,
               'matched_num': matched_num,'orig_num':orig_num}
    print(len(connection.queries))
    return [context,session_dict]


def get_dataset_params(user_genes_set, user_background_set, dataset, background_calc):
    
    if background_calc == "Intersect": 
        N = Annotation.objects.filter(Q(gene__in=user_background_set) & Q(cluster__dataset=dataset)).count()
        n = Annotation.objects.filter(Q(gene__in=user_genes_set) & Q(cluster__dataset=dataset)).count()
    else:
        N = user_background_set.count()
        n = user_genes_set.count()
    
    params = {'N': N, 'n': n, 'dataset_name': dataset.dataset_name}
    
    return params

def get_cluster_params(user_genes_set, user_background_set, cluster):
    
    K = Annotation.objects.filter(Q(gene__in=user_background_set) & Q(cluster=cluster)).count()
    k = Annotation.objects.filter(Q(gene__in=user_genes_set) & Q(cluster=cluster)).select_related('gene')
    
    overlap_genes = [anno.gene.gene_symbol for anno in k]
    k = k.count()
    
    params = {'K': K, 'k': k, 'overlap_genes': overlap_genes,
              'cluster_number': cluster.cluster_number,
              'cluster_name': cluster.cluster_description,
              'cluster_description': str(cluster),
              'dataset_name': cluster.dataset.dataset_name}
    
    return params


def compute_hypergeom(dataset_params, cluster_params, user_cluster):
    # compile dataset and cluster paramters
    compiled_params = [{**cluster_entry, **dataset_entry}
                        for cluster_entry in cluster_params
                        for dataset_entry in dataset_params
                        if cluster_entry['dataset_name'] == dataset_entry['dataset_name']]
    
    results = []
    
    for entry in compiled_params:
        if entry['k'] == 0:
            pval = 1
        else:
            pval = sp.hypergeom.sf(entry['k'], entry['N'], entry['n'], entry['K'])
        
        r = result_object(user_cluster, pval,
                          [entry['N'], entry['K'], entry['n'], entry['k']], entry['overlap_genes'])
        r.dataset_name = entry['dataset_name']
        r.cluster_number = entry['cluster_number']
        r.cluster_name = entry['cluster_name']
        r.cluster_description = entry['cluster_description']
        
        results.append(r)
        
    return results


def hypergeom_wrapper(user_genes, user_background,
                   user_choices, background_calc,
                   total, progress_recorder):

    results = list()
    missed_genes = dict()
    matched_gene_num = 0

    user_background_set = Gene.objects.filter(alias__alias_name__in=user_background)
    db_matched_bg = list(Alias.objects.filter(gene__in=user_background_set).values_list('alias_name', flat=True))
    missed_background = [x for x in user_background if x not in db_matched_bg]

    progress_recorder.set_progress(2, total)
    global progress
    progress = 2
    
    datasets = Dataset.objects.filter(pk__in=user_choices) # get user selected datasets
    clusters = Cluster.objects.filter(dataset__in=datasets).select_related() # get all associated clusters
    
    for user_cluster in user_genes:

        user_genes_converted = helper.user_convert(user_genes[user_cluster])
        user_genes_set = Gene.objects.filter(alias__alias_name__in=user_genes_converted[0])
        matched_gene_num = matched_gene_num + user_genes_set.count()

        # get missed genes
        missed_genes[user_cluster] = user_genes_converted[1]  # get unmapped ensembl IDs
        db_matched_g = list(Alias.objects.filter(gene__in=user_genes_set).values_list('alias_name', flat=True))
        db_nomatch_g = [x for x in user_genes_converted[0] if x not in db_matched_g]
        missed_genes[user_cluster].extend(db_nomatch_g)
        
        dataset_params = [ get_dataset_params(user_genes_set, user_background_set, dataset, background_calc)
                          for dataset in datasets.iterator() ]
        progress += 1
        progress_recorder.set_progress(progress, total)
        
        cluster_params = [ get_cluster_params(user_genes_set, user_background_set, cluster)
                          for cluster in clusters.iterator() ]
        progress += 1
        progress_recorder.set_progress(progress, total)
        
        
        hypergeom_results = compute_hypergeom(dataset_params, cluster_params, user_cluster)
        results.extend(hypergeom_results)
        
        progress += 1
        progress_recorder.set_progress(progress, total)
            
    pvals = [r.pval for r in results]
    adjusted_pvals = mt.multipletests(pvals, method="fdr_bh")[1]

    for r, p in zip(results, adjusted_pvals):
        r.adjusted_pval = p

        if r.pval <= 0.05:
            r.color = 'red'
        elif r.pval >= 0.95:
            r.color = 'blue'
        else:
            r.color = 'grey'

    return {'results': results, 'missed_genes': missed_genes,
            'missed_background': missed_background,
            'matched_gene_num': matched_gene_num,
            'matched_bg_num': user_background_set.count(),
            'progress': progress}
