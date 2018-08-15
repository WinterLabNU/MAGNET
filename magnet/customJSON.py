# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 11:28:56 2018

@author: USER
"""

from magnet_v030.result_object import result_object
    
import simplejson as json

class CustomEncoder(json.JSONEncoder):   
    def default(self, obj):
        if isinstance(obj, result_object):
            a = {"__type__":'__result_object__'}
            a.update(obj.__dict__)
            return a
        else:
            return json.JSONEncoder.default(self, obj)

def custom_decoder(obj):
    if '__type__' in obj:
        if obj['__type__']=='__result_object__':
            r = result_object(user_cluster = obj["user_cluster"],
                              pval = obj["pval"], 
                              parameters = [obj["N"],obj["B"],obj["n"],obj["b"]])
            r.dataset_name = obj['dataset_name'],
            r.cluster_number = obj['cluster_number'],
            r.cluster_name = obj['cluster_name'],
            r.cluster_description = obj['cluster_description']
            r.adjusted_pval = obj['adjusted_pval']
            r.color = obj['color']
            return r
    return obj

# Encoder function      
def custom_dumps(obj):
    return json.dumps(obj, cls=CustomEncoder, use_decimal = True)

# Decoder function
def custom_loads(obj):
    return json.loads(obj, object_hook=custom_decoder)