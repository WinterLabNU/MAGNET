from django.contrib import admin
from .models import Gene, Dataset, Cluster, Annotation,Alias
# Register your models here.

class ClusterInline(admin.TabularInline):
    model = Cluster

class DatasetAdmin(admin.ModelAdmin):
    list_display = ('dataset_name','journal')
    fieldsets=[
            (None, {'fields': ['dataset_name','full_title','authors','abstract','publication_date',
                               'journal','link_to_pubmed']}),
    ]
    
    #def format_date(self, obj):
        #return obj.publication_date.strftime('%b, %Y')
    
    #format_date.short_description = 'Publication Date'
    
    inlines = [ClusterInline]

    search_fields = ['dataset_name']
    
class AliasInline(admin.TabularInline):
    model = Alias

class GeneAdmin(admin.ModelAdmin):
    inlines = [AliasInline]
    search_fields = ['gene_symbol']
    
class AnnotationAdmin(admin.ModelAdmin):
    search_fields = ['gene']
    
admin.site.register(Dataset,DatasetAdmin)
admin.site.register(Gene, GeneAdmin)
admin.site.register(Annotation, AnnotationAdmin)