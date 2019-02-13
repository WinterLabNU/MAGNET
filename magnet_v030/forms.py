from django import forms
from .models import Dataset


class UserForm(forms.Form):

    # radio button to ask whether the user is submitting one or multiple query gene lists
    one_or_multiple = forms.ChoiceField(label='',
                                        choices=[('One', 'One'),
                                                 ('Multiple', 'Multiple')],
                                        widget=forms.RadioSelect, required=False)

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
                                        widget=forms.RadioSelect, required=False)

    # checkboxes for datasets to include
    user_selected_datasets = forms.ModelChoiceField(queryset=Dataset.objects.all(),
                                                    empty_label=None,
                                                    label='Include the following datasets from the database :',
                                                    required=False,
                                                    widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['user_selected_datasets'].choices = [(dataset.id, dataset.dataset_name) for dataset in Dataset.objects.all()]

    # def clean(self):
        # cleaned_data = super(UserForm,self).clean()
        # user_genes = cleaned_data.get('user_genes')
        # user_background = cleaned_data.get('user_background')
        # user_selected_datasets = cleaned_data.get('user_selected_datasets')

        # if not user_genes and not user_background and not user_selected_datasets:
            # raise forms.ValidationError('Please fill all the input values for enrichment calculation!')
