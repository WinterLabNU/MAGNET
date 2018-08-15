# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 13:49:27 2018

@author: USER
"""

def handle_csv(csv_file):
    
   file_data = csv_file.read().decode("utf-8")        
   lines = file_data.split("\n")
   gene_list = []
   
   for line in lines:
       fields = line.split(",")
       if fields[0].strip() != 'Symbols':
            gene_list.append(fields[0].strip())
            
   return gene_list