# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 11:19:15 2018

@author: USER
"""
# Full path and name to your csv file 
csv_path="D:/research/magnet/magnet_0.6.1/data/sasha_data.csv" 

# Full path to your django project directory 
magnet_home="D:/research/magnet/magnet_0.6.1/"

 
import sys,os, django
sys.path.append(magnet_home) 
os.environ['DJANGO_SETTINGS_MODULE'] = 'magnet.settings' 
django.setup()

from magnet_v030.models import Gene, Dataset, Cluster, Annotation, Alias
from django.db import transaction
from convert import convert

existing = []
for alias in Alias.objects.all():
    if alias.alias_name in existing:
        print(alias.alias_name)
        alias.delete()
    else:
        existing.append(alias.alias_name)
        