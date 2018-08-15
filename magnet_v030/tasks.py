# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 15:38:53 2018

@author: USER
"""

# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import task
from celery_progress.backend import ProgressRecorder
from . import helper
import json
from .models import Gene, Dataset, Cluster, Annotation


@task(bind=True)
def task_wrapper(self,user_data):
    
    progress_recorder = ProgressRecorder(self)
    
    user_genes,user_background,user_choices,background_calc = user_data
    
    total = len(user_genes)*len(user_choices) + len(user_genes)+ 2
    progress_recorder.set_progress(0, total)
    
    user_background_converted = helper.user_convert(user_background)
    progress_recorder.set_progress(1, total)
    
    hg_output = helper.hypergeom_test(user_genes, user_background_converted[0], 
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
    for d in Dataset.objects.filter(dataset_name__in=user_choices):
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
    
    return [context,session_dict]