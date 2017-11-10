from django import forms
from .models import Printer
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class PrinterForm(forms.ModelForm):
    name = forms.CharField(label='Printer Name', max_length=200,widget=forms.TextInput(attrs={'class': "input-lg"}))
    code = forms.CharField(label='Printer Code', max_length=10,widget=forms.TextInput(attrs={'class': "input-lg"}))    
    description = forms.CharField(label='Printer Description')
    
class PatientForm(forms.ModelForm):
    name = forms.CharField(label='Printer Name', max_length=200,widget=forms.TextInput(attrs={'class': "input-lg"}))
    code = forms.CharField(label='Printer Code', max_length=10,widget=forms.TextInput(attrs={'class': "input-lg"}))    
    description = forms.CharField(label='Printer Description')
    
class ClinicianForm(forms.ModelForm):
    name = forms.CharField(label='Printer Name', max_length=200,widget=forms.TextInput(attrs={'class': "input-lg"}))
    code = forms.CharField(label='Printer Code', max_length=10,widget=forms.TextInput(attrs={'class': "input-lg"}))    
    description = forms.CharField(label='Printer Description')
    
class LabItemTypeForm(forms.ModelForm):
    name = forms.CharField(label='Printer Name', max_length=200,widget=forms.TextInput(attrs={'class': "input-lg"}))
    code = forms.CharField(label='Printer Code', max_length=10,widget=forms.TextInput(attrs={'class': "input-lg"}))    
    description = forms.CharField(label='Printer Description')

class CollectionTypeForm(forms.ModelForm):
    name = forms.CharField(label='Printer Name', max_length=200,widget=forms.TextInput(attrs={'class': "input-lg"}))
    code = forms.CharField(label='Printer Code', max_length=10,widget=forms.TextInput(attrs={'class': "input-lg"}))    
    description = forms.CharField(label='Printer Description')
    
class OrthoModoJobForm(forms.ModelForm):
    orthotrac_analysis_notes = forms.CharField(label='Orthotrac ANalysis Notes')
    
class LabItemForm(forms.ModelForm):
    is_blocked = forms.CharField(label='Printer Name', max_length=200,widget=forms.TextInput(attrs={'class': "input-lg"}))

    