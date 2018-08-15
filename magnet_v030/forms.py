from django import forms
from .models import Dataset

class UserForm(forms.Form):
    
    one_or_multiple = forms.ChoiceField(label='',choices=[('One','One'),("Multiple",'Multiple')],
                                        widget=forms.RadioSelect,required=False)
    
    user_genes = forms.CharField(label='Gene List:',required = False, widget=forms.Textarea(attrs={'placeholder': 'Enter your list of query genes here','rows':4,'cols':15}))
    user_genes_upload = forms.FileField(label="", required = False)
    
    user_background = forms.CharField(label='Background:',required = False, widget=forms.Textarea(attrs={'placeholder': 'Enter your list of background genes here','rows':4,'cols':15}))
    ##
    background_calc = forms.ChoiceField(label='',choices=[('Intersect','Intersect'),("User",'User')],
                                        widget=forms.RadioSelect, required=False)
    
    user_background_upload = forms.FileField(label="", required = False)
    
    user_selected_datasets = forms.ModelChoiceField(queryset= Dataset.objects.all(),empty_label=None,label='Include the following datasets from the database :',required=False,widget=forms.HiddenInput())
    
    def __init__(self,*args,**kwargs):
        super(UserForm,self).__init__(*args,**kwargs)
        self.fields['user_selected_datasets'].choices = [(e.id,e.dataset_name) for e in Dataset.objects.all()]


    #def clean(self):
        #cleaned_data = super(UserForm,self).clean()
        #user_genes = cleaned_data.get('user_genes')
        #user_background = cleaned_data.get('user_background')
        #user_selected_datasets = cleaned_data.get('user_selected_datasets')

        #if not user_genes and not user_background and not user_selected_datasets:
            #raise forms.ValidationError('Please fill all the input values for enrichment calculation!')
