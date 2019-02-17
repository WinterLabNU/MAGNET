from django import forms
from .models import Dataset


class UserForm(forms.Form):

    # radio button to ask whether the user is submitting one or multiple query gene lists
    one_or_multiple = forms.ChoiceField(label='',
                                        choices=[('One', 'One'),
                                                 ('Multiple', 'Multiple')],
                                        widget=forms.RadioSelect, required=True)

    # text area for pasting a single query gene list
    user_genes = forms.CharField(label='Gene List:',
                                 required=False,
                                 widget=forms.Textarea(attrs={'placeholder': 'Enter your list of query genes here',
                                                              'rows': 4, 'cols': 15}))

    # file upload for query gene lists
    user_genes_upload = forms.FileField(label="", required=False)

    # text area for pasting a background gene list
    user_background = forms.CharField(label='Background:',
                                      required=False,
                                      widget=forms.Textarea(attrs={'placeholder': 'Enter your list of background genes here',
                                                                   'rows': 4,
                                                                   'cols': 15}))

    # file upload for the background gene list
    user_background_upload = forms.FileField(label="", required=False)

    # radio button for background processing modes
    background_calc = forms.ChoiceField(label='',
                                        choices=[('Intersect', 'Intersect'), ("User", 'User')],
                                        widget=forms.RadioSelect, required=True)

    # checkboxes for datasets to include
    dataset_choices = [(dataset.id, dataset.dataset_name) for dataset in Dataset.objects.all()]
    user_selected_datasets = forms.MultipleChoiceField(choices=dataset_choices,
                                                    label='Include the following datasets from the database :',
                                                    required=True,
                                                    error_messages={'required': 'Please select at least one dataset!'},
                                                    widget=forms.CheckboxSelectMultiple)


    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        
        user_genes_upload = cleaned_data.get("user_genes_upload")
        user_background_upload = cleaned_data.get("user_background_upload")
        user_genes = cleaned_data.get('user_genes')
        user_background = cleaned_data.get('user_background')
        
        if not user_genes and not user_genes_upload:
            raise forms.ValidationError('Please submit at least one query gene list!')
            
        if not user_background and not user_background_upload:
            raise forms.ValidationError('Plaase submit the background gene list!')

