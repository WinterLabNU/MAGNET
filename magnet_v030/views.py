from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Gene, Dataset, Cluster, Annotation
from .forms import UserForm
from . import helper
import json
from .tasks import task_wrapper
#from celery.result import AsyncResult

def index(request):
    # the number of gene and dataset entries
    database_numbers = [Gene.objects.count(), Dataset.objects.count()]
    database_values = [Dataset.objects.values('dataset_name')]

    dataset_list = []
    for sampl in database_values:
        for k in sampl:
            dataset_list.append([f[0] for g,f in k.items()])

    form = UserForm()
    context = {'database_numbers': database_numbers, 'dataset_list': dataset_list,'form':form}

    return render(request,'magnet_v030/index.html',context)

def processing(request):
    
    user_data = helper.input_handler(request)
    
    if len(user_data[0]) == 0 or len(user_data[1]) == 0 or len(user_data[2]) == 0:
        form = UserForm(request.POST,request.FILES or None)
        print("ERROR! PLEASE CHECK THE INPUT")
        error_message = 'Please enter your gene list, background and dataset choices!'
        return render(request, 'magnet_v030/index.html', {'form':form, 'error_message':error_message})
    
    magnet_task = task_wrapper.delay(user_data)
    
    request.session['magnet_task_id'] = magnet_task.id

    return render(request, 'magnet_v030/display_progress.html', context={'task_id': magnet_task.task_id})
    
            
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
        
        print(celery_result[1])
        
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