# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 10:45:21 2018

@author: USER
"""
#import json

class result_object:
    
    adjusted_pval = None
    color = None
    dataset_name = None
    cluster_number = None
    cluster_name = None
    cluster_description = None
    
    def __init__(self, user_cluster, pval, parameters, overlap_genes):
        
        self.user_cluster = user_cluster
        self.pval = pval
        self.N, self.B, self.n, self.b = parameters
        self.overlap_genes = overlap_genes
        
    def __str__(self):
        
        str_info = [str(self.dataset_name), str(self.cluster_number), self.cluster_description, self.color, str(self.overlap_genes)]
        return ','.join(str_info)
    
    #def toJSON(self):
        #return json.dumps(self, default=lambda o: o.__dict__, 
            #sort_keys=True, indent=4)