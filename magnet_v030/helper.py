# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 13:49:27 2018

@author: USER
"""

from __future__ import absolute_import, unicode_literals
from django.shortcuts import render
from django.utils.translation import ugettext
from django.db.models import Q
import xlsxwriter as xl
import mygene
import scipy.stats as sp
import statsmodels.sandbox.stats.multicomp as mt
from io import BytesIO
import re

from .models import Gene, Dataset, Cluster, Annotation, Alias
from .forms import UserForm
from .result_object import result_object

def form_processing(form):
    
    one_or_multiple = form.cleaned_data.get('one_or_multiple')
    background_calc = form.cleaned_data.get('background_calc')
    user_choices = form.cleaned_data.get('user_selected_datasets')
    user_choices = [int(i) for i in user_choices]  # convert str to int
    print(one_or_multiple)
    print(background_calc)
    print(user_choices)

    user_genes = form.cleaned_data.get('user_genes')
    user_background = form.cleaned_data.get('user_background')
    user_genes_upload = form.cleaned_data.get("user_genes_upload")
    user_background_upload = form.cleaned_data.get("user_background_upload")
    
    if user_genes_upload:
        user_genes = handle_csv(user_genes_upload, one_or_multiple, False)
    else:
        user_genes = list(filter(None, form.cleaned_data['user_genes'].split("\n")))
        user_genes = {1: [a.strip().upper() for a in user_genes]}

    if user_background_upload:
        user_background = list(filter(None, handle_csv(user_background_upload, one_or_multiple, True)))
    else:
        user_background = list(filter(None, form.cleaned_data['user_background'].split("\n")))
        user_background = [b.strip().upper() for b in user_background]

    return [user_genes, user_background, user_choices, background_calc]


def handle_csv(csv_file, one_or_multiple, background):

    file_data = csv_file.read().decode("utf-8")
    lines = file_data.split("\n")

    if one_or_multiple == "One" or background:
        gene_list = []

        for line in lines:
            fields = line.split(",")
            if fields[0].strip() != 'Symbols' and line != '':
                gene_list.append(fields[0].strip().upper())

        if not background:
            gene_list = {1: gene_list}

    else:

        gene_list = {}

        for line in lines:
            fields = line.split(",")

            if fields[0].strip() != 'Symbols' and line != '':

                if fields[1].strip() not in gene_list:
                    gene_list[fields[1].strip()] = [fields[0].strip().upper()]
                else:
                    gene_list[fields[1].strip()].append(fields[0].strip().upper())

    return gene_list


def hypergeom_test(user_genes, user_background,
                   user_choices, background_calc,
                   total, progress_recorder):

    results = list()
    missed_genes = dict()
    matched_gene_num = 0

    user_background_set = Gene.objects.filter(alias__alias_name__in=user_background)
    db_matched_bg = list(Alias.objects.filter(gene__in=user_background_set).values_list('alias_name', flat=True))
    missed_background = [x for x in user_background if x not in db_matched_bg]

    progress_recorder.set_progress(2, total)
    progress = 2

    for user_cluster in user_genes:

        user_genes_converted = user_convert(user_genes[user_cluster])
        user_genes_set = Gene.objects.filter(alias__alias_name__in=user_genes_converted[0])
        matched_gene_num = matched_gene_num + user_genes_set.count()

        # get missed genes
        missed_genes[user_cluster] = user_genes_converted[1]  # get unmapped ensembl IDs
        db_matched_g = list(Alias.objects.filter(gene__in=user_genes_set).values_list('alias_name', flat=True))
        db_nomatch_g = [x for x in user_genes_converted[0] if x not in db_matched_g]
        missed_genes[user_cluster].extend(db_nomatch_g)

        progress += 1
        progress_recorder.set_progress(progress, total)

        for d in Dataset.objects.filter(pk__in=user_choices):
            clusters = Cluster.objects.filter(dataset=d)

            # print(background_calc)
            if background_calc == "Intersect":
                N = Annotation.objects.filter(Q(gene__in=user_background_set) & Q(cluster__dataset=d)).count()
                n = Annotation.objects.filter(Q(gene__in=user_genes_set) & Q(cluster__dataset=d)).count()
            else:
                N = user_background_set.count()
                n = user_genes_set.count()

            progress += 1
            progress_recorder.set_progress(progress, total)

            for c in clusters:

                B = Annotation.objects.filter(Q(gene__in=user_background_set) & Q(cluster=c)).count()
                b = Annotation.objects.filter(Q(gene__in=user_genes_set) & Q(cluster=c))
                overlap_genes = [anno.gene.gene_symbol for anno in b]
                # print(overlap_genes)
                b = b.count()

                if b == 0:
                    pval = 1
                else:
                    pval = sp.hypergeom.sf(b, N, n, B)

                r = result_object(user_cluster, pval, [N, B, n, b], overlap_genes)
                r.dataset_name = str(d)
                r.cluster_number = c.cluster_number
                r.cluster_name = c.cluster_description
                r.cluster_description = str(c)

                results.append(r)

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


def convert_keys_toStr(dictionary):

    if not isinstance(dictionary, dict):
        return dictionary
    return dict((str(k), convert_keys_toStr(v)) for k, v in dictionary.items())


def write_to_xlworksheet(results_dict, worksheet_name=None):

    # Open stream channel for xlsxwriter
    outstream = BytesIO()
    workbuk = xl.Workbook(outstream)
    worksheet = workbuk.add_worksheet(worksheet_name)

    # Define Excel Styles
    title = workbuk.add_format({
        'bold': True,
        'bg_color': 'yellow',
        'color': 'blue',
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })

    header = workbuk.add_format({
        'bg_color': '#FFDBDB',
        'color': 'black',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })

    cell = workbuk.add_format({
        'align': 'left',
        'valign': 'vcenter',
        'bg_color': '#FFEFEF',
        'text_wrap': True,
        'border': 1
    })

    cell_center = workbuk.add_format({
        'align': 'center',
        'bg_color': '#FFEFEF',
        'valign': 'vcenter',
        'border': 1
    })

    # Write Worksheet Title
    if worksheet_name:
        title_name = worksheet_name
    else:
        title_name = 'Worksheet1'

    worksheet_title = "{0} {1}".format(ugettext("GO Enrichment Report for"), title_name)
    worksheet.merge_range('B2:I2', worksheet_title, title)

    # Write headers for the output table
    worksheet.write(4, 2, ugettext("No."), header)
    worksheet.write(4, 3, ugettext("Dataset"), header)
    worksheet.write(4, 4, ugettext("Cluster"), header)
    worksheet.write(4, 5, ugettext("P-Value"), header)
    worksheet.write(4, 6, ugettext("Adjusted P-Value(FDR)"), header)
    worksheet.write(4, 7, ugettext("Input Parameters(N,B,n,b)"), header)

    # Change column widths
    worksheet.set_column('D:D', 30)
    worksheet.set_column('E:E', 40)
    worksheet.set_column('F:F', 20)
    worksheet.set_column('G:G', 25)
    worksheet.set_column('H:H', 25)

    # Write data to the worksheet
    idx = 4
    inc = 1

    for key, val in results_dict.items():

        row = idx + inc

        dataset = ((key.split("('"))[1].split("',")[0])
        cluster = ((key.split(",")[1]).split("'")[1].split("')")[0])

        # Define cell values to write
        idx_num = inc
        pvalue = val[0]
        adj_pvalue = val[1]
        N = val[2]
        B = val[3]
        n = val[4]
        b = val[5]
        input_parameters = str(N)+" , "+str(B)+" , "+str(n)+" , "+str(b)

        # Write cell values to the worksheet
        worksheet.write_number(row, 2, idx_num, cell_center)
        worksheet.write_string(row, 3, dataset, cell)
        worksheet.write_string(row, 4, cluster, cell)
        worksheet.write_number(row, 5, pvalue, cell_center)
        worksheet.write_number(row, 6, adj_pvalue, cell_center)
        worksheet.write_string(row, 7, input_parameters, cell_center)

        inc += 1

    workbuk.close()
    xl_data = outstream.getvalue()

    return xl_data


def user_convert(gene_list):
    mg = mygene.MyGeneInfo()

    query = []
    remaining = gene_list.copy()
    for e in gene_list:
        if e.startswith("ENSMUSG"):
            query.append(e)
            remaining.remove(e)

    query_results = mg.querymany(query, scopes='ensemblgene', fields='symbol', species='mouse')

    converted_symbols = []
    seen, unmapped = [], []

    for d in query_results:
        if 'notfound' in d:
            unmapped.append(d['query'].upper())
        elif d['query'] in seen:
            pass
        else:
            converted_symbols.append(d['symbol'].upper())
            seen.append(d['query'])

    converted_gene_list = remaining + converted_symbols

    return [converted_gene_list, unmapped]


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):

    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
    and grouping quoted words together.
    Example:

    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
    ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''

    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):

    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)

    for term in terms:
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if query is None:
                query = q
            else:
                query = query | q
    return query
