from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Gene, Dataset, Cluster, Annotation
from .forms import UserForm
from . import helper
import json
from .tasks import task_wrapper
from .helper import normalize_query, get_query
#from celery.result import AsyncResult

def index(request):
    
    # retrieve the number of gene and dataset entries in MAGNET database
    database_numbers = [Gene.objects.count(), Dataset.objects.count()]
    # retrieve the names of datasets in MAGNET database
    dataset_list = Dataset.objects.values_list('dataset_name', flat=True)
    
    form = UserForm()
    context = {'database_numbers': database_numbers, 'dataset_list': dataset_list, 'form': form}
    
    return render(request, 'magnet_v030/index.html', context)

def processing(request):
    
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = UserForm(request.POST, request.FILES)
        
        # Check if the form is valid:
        if form.is_valid():
            
            # parse form
            user_data = helper.form_processing(form)
            
            # call celery task
            magnet_task = task_wrapper.delay(user_data)
            request.session['magnet_task_id'] = magnet_task.id

            return render(request, 'magnet_v030/display_progress.html', context={'task_id': magnet_task.task_id})
    
    else:
        
        form = UserForm()
        
    # retrieve the number of gene and dataset entries in MAGNET database
    database_numbers = [Gene.objects.count(), Dataset.objects.count()]
    # retrieve the names of datasets in MAGNET database
    dataset_list = Dataset.objects.values_list('dataset_name', flat=True) 
    
    print(form.errors)
    
    context = {'database_numbers': database_numbers, 'dataset_list': dataset_list, 'form': form}
    
    return render(request, 'magnet_v030/index.html', context)
    
def results(request):
    
    task_id = request.session.get('magnet_task_id')
    magnet_task = task_wrapper.AsyncResult(task_id)
    
    if magnet_task.state == 'SUCCESS':
        celery_result = magnet_task.get()
        request.session['session_data'] = celery_result[1]
        
        context = celery_result[0]
        dataset_dict = context['dataset_dict']
        new_dataset_dict = {}
        
        for k,v in dataset_dict.items():
            d = Dataset.objects.get(pk=k)
            new_dataset_dict[d] = v
            
        context.pop('dataset_dict')
        context['dataset_dict'] = new_dataset_dict
        
        #print(context['sig_results'][0])
        
        return render(request,'magnet_v030/magnet_results.html', context)
    else:
        return HttpResponse("Something went wrong!")
    

def download_inExcel(request):

    #Get session request to obtain data
    session_data = request.session.get('session_data')
    
    print(session_data)
    
    #Load the JSON data back from the Sessions Middleware
    session_data = json.loads(session_data)
    print("Signal Received and data loaded!!!")

    #Write output data to Excel Workbook
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Magnet_Report.xlsx'

    excel_data = helper.write_to_xlworksheet(session_data,"WorkSheet_test")
    response.write(excel_data)
    return response
    

def dataset_info(request, dataset_id):
    
    dataset = get_object_or_404(Dataset, pk = dataset_id)
    
    clusters = Cluster.objects.filter(dataset=dataset)
    cluster_gene_num = {}

    # get number of genes associated with each cluster
    for c in clusters:
        anno_num = Annotation.objects.filter(cluster=c).count()
        cluster_gene_num[c] = anno_num
        
    total_gene_num = sum(cluster_gene_num.values())

    context = {'dataset':dataset,'cluster_gene_num':cluster_gene_num, 'total_gene_num':total_gene_num}
            
    return render(request,'magnet_v030/dataset_info.html', context)

def documentation(request):
    
    if request.method=='GET':
        page = request.GET.get('page')
        print(page)
        if not page:
            return HttpResponse('<h1>Page not found</h1>')
        else:
            if page == "usage":
                nav = ("active","","")
                content = ("active","fade","fade")
            elif page == "faq":
                nav = ("","active","")
                content = ("fade","active","fade")
            else:
                nav = ("","","active")
                content = ("fade","fade","active")
            
    context = {'nav':nav,'content':content}
    return render(request,'magnet_v030/documentation.html', context)

def search(request):
    query_string = ''
    found_entries = None
    #if ('q' in request.GET) and request.GET['q'].strip():
    if request.GET.get('search'):
        query_string = request.GET.get('search')
        #query_string = request.GET['q']
        print(query_string)

        entry_query = get_query(query_string, ['gene__alias__alias_name',])
        print(entry_query)

        found_entries = Annotation.objects.filter(entry_query)
        print(found_entries)
    
    else: 
        print("False")
    return render(request,'magnet_v030/search.html',
                      { 'query_string': query_string, 'found_entries': found_entries})