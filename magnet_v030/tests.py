from django.test import TestCase, Client
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import *   # import all forms
from .models import Gene, Dataset, Cluster, Annotation

# Create your tests here.

class IndexViewTest(TestCase):
    
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/magnet/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get('/magnet/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'magnet_v030/index.html')
    
class UserFormTest(TestCase):
    
    def test_UserForm_valid(self):
        form = UserForm(data={'one_or_multiple': "One", 'user_genes': "Abcd", 'user_genes_upload': "", 'user_background':"Abcd",
                             'user_background_upload':"", 'user_selected_datasets':""})
        self.assertTrue(form.is_valid())
        
    def test_UserForm_invalid(self):
        form = UserForm(data={'one_or_multiple': None, 'user_genes': "", 'user_genes_upload': "", 'user_background':"Abcd",
                             'user_background_upload':"", 'user_selected_datasets':""})
        self.assertFalse(form.is_valid())