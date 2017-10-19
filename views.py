from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.views.generic import DetailView
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
#from django.contrib.auth.forms import UserCreationForm
import math
import sys
import datetime

from django.db import connections
from django.db.models import Count, Min, Sum, Avg, F, Q
from django.http import JsonResponse

from functools import reduce
import operator


from .models import Printer, Patient, Clinician, OrthoModelType, CollectionType, OrthoModoJob

from orthomodoweb.forms import PrinterForm, PatientForm, ClinicianForm,OrthoModelTypeForm, CollectionTypeForm, OrthoModoJobForm


#***************HOME PAGE***********
class HomeView(generic.TemplateView):
    template_name = 'orthomodoweb/home.html'
    
#**************SIGNUP*****************
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('orthomodoweb:home')
    else:
        return redirect('orthomodoweb:home')

#**************OrthoModoJob*****************
class OrthoModoJobViewOpen(LoginRequiredMixin,generic.ListView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = OrthoModoJob
    template_name = 'orthomodoweb/orthomodojob/orthomodojob_open_list.html'
    def get_context_data(self, **kwargs):
        context=super(OrthoModoJobViewOpen,self).get_context_data(**kwargs)
        context['total_open_jobs'] =  OrthoModoJob.objects.filter(Q(flagged=True) | Q(is_collected=False)).count() 
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            print('Searching for ', file=sys.stderr)
            print('-'.join(query_list), file=sys.stderr)
            context['search_applied'] = '-'.join(query_list)
        return context
    def get_queryset(self):
        """Return open OrthoModoJobs for the logged-in user."""
        print('Open jobs list', file=sys.stderr)
        result = OrthoModoJob.objects.filter(Q(flagged=True) | Q(is_collected=False)).order_by('-scan_date') 
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(patient__name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(clinician__name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(scan_date__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(orthotrac_analysis_notes__icontains=q) for q in query_list)) |    
                reduce(operator.and_,
                       (Q(printer__name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(print_date__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(orthomodel_type__name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(orthomodel_notes__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(collection_type__name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(planned_collection_date__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(collection_notes__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(flag_status_note__icontains=q) for q in query_list))
            )
        return result
        
class OrthoModoJobViewAll(LoginRequiredMixin,generic.ListView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = OrthoModoJob
    template_name = 'orthomodoweb/orthomodojob/orthomodojob_all_list.html'
    def get_context_data(self, **kwargs):
        context=super(OrthoModoJobViewAll,self).get_context_data(**kwargs)
        context['total_all_jobs'] =  OrthoModoJob.objects.filter().count() 
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            print('Searching for ', file=sys.stderr)
            print('-'.join(query_list), file=sys.stderr)
            context['search_applied'] = '-'.join(query_list)
        return context
    def get_queryset(self):
        """Return all OrthoModoJobs."""
        result = OrthoModoJob.objects.filter().order_by('-scan_date') 
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(patient__name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(clinician__name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(scan_date__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(orthotrac_analysis_notes__icontains=q) for q in query_list)) |    
                reduce(operator.and_,
                       (Q(printer__name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(print_date__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(orthomodel_type__name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(orthomodel_notes__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(collection_type__name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(planned_collection_date__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(collection_notes__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(flag_status_note__icontains=q) for q in query_list))
            )
        return result

class OrthoModoJobCreate(LoginRequiredMixin,CreateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = OrthoModoJob
    form = OrthoModoJobForm
    template_name = 'orthomodoweb/orthomodojob/orthomodojob_add_form.html'
    fields=['patient','clinician','scan_date','orthotrac_reference_no','orthotrac_analysis_done','orthotrac_analysis_notes','printer','is_stl_file_prepared','is_printed','print_date','orthomodel_type','orthomodel_notes','collection_type','planned_collection_date','planned_collection_time','collection_notes','is_collected','flagged','flag_status_note']   
    def form_valid(self, form):
        orthomodojob = form.save(commit=False)
        orthomodojob.user = self.request.user
        return super(OrthoModoJobCreate, self).form_valid(form)

class OrthoModoPatientJobCreate(LoginRequiredMixin,CreateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = OrthoModoJob
    form = OrthoModoJobForm
    template_name = 'orthomodoweb/patient/patient_add_job_form.html'
    fields=['clinician','scan_date','orthotrac_reference_no','orthotrac_analysis_done','orthotrac_analysis_notes','printer','is_stl_file_prepared','is_printed','print_date','orthomodel_type','orthomodel_notes','collection_type','planned_collection_date','planned_collection_time','collection_notes','is_collected','flagged','flag_status_note']   
    def form_valid(self, form):
        print('save new job', file=sys.stderr)
        print(form.data['selected_patient_id'], file=sys.stderr)
        orthomodojob = form.save(commit=False)
        orthomodojob.user = self.request.user
        selected_patient_id = form.data['selected_patient_id']
        patient = get_object_or_404(Patient, id=selected_patient_id)
        orthomodojob.patient = patient
        return super(OrthoModoPatientJobCreate, self).form_valid(form)
    def form_invalid(self, form):
        print('save new job INVALID', file=sys.stderr)
        print(form.errors, file=sys.stderr)
        return HttpResponse("form is invalid... " + str(form.errors))
    def get_context_data(self, **kwargs):
        context=super(OrthoModoPatientJobCreate,self).get_context_data(**kwargs)
        context['selected_patient'] = get_object_or_404(Patient, id=self.kwargs['patient_id'])
        print(context['selected_patient'], file=sys.stderr)
        context['clinician_list'] =  Clinician.objects.all()
        context['printer_list'] =  Printer.objects.all()
        context['orthomodel_type_list'] =  OrthoModelType.objects.all()
        context['collection_type_list'] =  CollectionType.objects.all()
        return context

class OrthoModoJobUpdate(LoginRequiredMixin,UpdateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = OrthoModoJob
    form = OrthoModoJobForm
    template_name = 'orthomodoweb/orthomodojob/orthomodojob_form.html'
    fields=['patient','clinician','scan_date','orthotrac_reference_no','orthotrac_analysis_done','orthotrac_analysis_notes','printer','is_stl_file_prepared','is_printed','print_date','orthomodel_type','orthomodel_notes','collection_type','planned_collection_date','planned_collection_time','collection_notes','is_collected','flagged','flag_status_note']   
    def get_queryset(self):
        base_qs = super(OrthoModoJobUpdate, self).get_queryset()
        return base_qs.filter()
    def get_context_data(self, **kwargs):
        context=super(OrthoModoJobUpdate,self).get_context_data(**kwargs)
        context['patient_list'] =  Patient.objects.all()
        context['clinician_list'] =  Clinician.objects.all()
        context['printer_list'] =  Printer.objects.all()
        context['orthomodel_type_list'] =  OrthoModelType.objects.all()
        context['collection_type_list'] =  CollectionType.objects.all()
        #print(context['patient_list'], file=sys.stderr)
      
        return context
    def form_invalid(self, form):
        print('save new job INVALID', file=sys.stderr)
        print(form.errors, file=sys.stderr)
        return HttpResponse("form is invalid... " + str(form.errors))

class OrthoModoJobDelete(LoginRequiredMixin,DeleteView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = OrthoModoJob
    template_name = 'orthomodoweb/orthomodojob/orthomodojob_confirm_delete.html'
    success_url = reverse_lazy('orthomodoweb:orthomodojob-open-list')
    def get_queryset(self):
        base_qs = super(OrthoModoJobDelete, self).get_queryset()
        return base_qs.filter()
        
#**************PRINTERS*****************
class PrinterView(LoginRequiredMixin,generic.ListView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Printer
    template_name = 'orthomodoweb/printer/printer_list.html'
    def get_queryset(self):
        """Return Printers for the logged-in user."""
        return Printer.objects.filter().order_by('name')  

class PrinterCreate(LoginRequiredMixin,CreateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Printer
    form = PrinterForm
    template_name = 'orthomodoweb/printer/printer_add_form.html'
    fields=['name','code','description']   
    def form_valid(self, form):
        printer = form.save(commit=False)
        printer.user = self.request.user
        return super(PrinterCreate, self).form_valid(form)

class PrinterUpdate(LoginRequiredMixin,UpdateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Printer
    form = PrinterForm
    template_name = 'orthomodoweb/printer/printer_form.html'
    fields=['name','code','description']   
    def get_queryset(self):
        base_qs = super(PrinterUpdate, self).get_queryset()
        return base_qs.filter()

class PrinterDelete(LoginRequiredMixin,DeleteView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Printer
    template_name = 'orthomodoweb/printer/printer_confirm_delete.html'
    success_url = reverse_lazy('orthomodoweb:printer-list')
    def get_queryset(self):
        base_qs = super(PrinterDelete, self).get_queryset()
        return base_qs.filter()

#**************PATIENTS*****************
class PatientView(LoginRequiredMixin,generic.ListView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Patient
    template_name = 'orthomodoweb/patient/patient_list.html'
    def get_queryset(self):
        """Return Patients for the logged-in user."""
        return Patient.objects.filter().order_by('name')  

class PatientCreate(LoginRequiredMixin,CreateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Patient
    form = PatientForm
    template_name = 'orthomodoweb/patient/patient_add_form.html'
    fields=['name','code','reference_no','email','phone_no_1','phone_no_2','address','dob','description']   
    def form_valid(self, form):
        patient = form.save(commit=False)
        patient.user = self.request.user
        return super(PatientCreate, self).form_valid(form)

class PatientUpdate(LoginRequiredMixin,UpdateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Patient
    form = PatientForm
    template_name = 'orthomodoweb/patient/patient_form.html'
    fields=['name','code','reference_no','email','phone_no_1','phone_no_2','address','dob','description']   
    def get_queryset(self):
        base_qs = super(PatientUpdate, self).get_queryset()
        return base_qs.filter()

class PatientDelete(LoginRequiredMixin,DeleteView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Patient
    template_name = 'orthomodoweb/patient/patient_confirm_delete.html'
    success_url = reverse_lazy('orthomodoweb:patient-list')
    def get_queryset(self):
        base_qs = super(PatientDelete, self).get_queryset()
        return base_qs.filter()
        
#**************CLINICIAN*****************
class ClinicianView(LoginRequiredMixin,generic.ListView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Clinician
    template_name = 'orthomodoweb/clinician/clinician_list.html'
    def get_queryset(self):
        """Return Clinicians for the logged-in user."""
        return Clinician.objects.filter().order_by('name')  

class ClinicianCreate(LoginRequiredMixin,CreateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Clinician
    form = ClinicianForm
    template_name = 'orthomodoweb/clinician/clinician_add_form.html'
    fields=['code','name','description']   
    def form_valid(self, form):
        clinician = form.save(commit=False)
        clinician.user = self.request.user
        return super(ClinicianCreate, self).form_valid(form)

class ClinicianUpdate(LoginRequiredMixin,UpdateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Clinician
    form = ClinicianForm
    template_name = 'orthomodoweb/clinician/clinician_form.html'
    fields=['code','name','description']    
    def get_queryset(self):
        base_qs = super(ClinicianUpdate, self).get_queryset()
        return base_qs.filter()

class ClinicianDelete(LoginRequiredMixin,DeleteView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Clinician
    template_name = 'orthomodoweb/clinician/clinician_confirm_delete.html'
    success_url = reverse_lazy('orthomodoweb:clinician-list')
    def get_queryset(self):
        base_qs = super(ClinicianDelete, self).get_queryset()
        return base_qs.filter()
        
#**************OrthoModelType*****************
class OrthoModelTypeView(LoginRequiredMixin,generic.ListView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = OrthoModelType
    template_name = 'orthomodoweb/orthomodeltype/orthomodeltype_list.html'
    def get_queryset(self):
        """Return OrthoModelTypes for the logged-in user."""
        return OrthoModelType.objects.filter().order_by('name')  

class OrthoModelTypeCreate(LoginRequiredMixin,CreateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = OrthoModelType
    form = OrthoModelTypeForm
    template_name = 'orthomodoweb/orthomodeltype/orthomodeltype_add_form.html'
    fields=['code','name','description']   
    def form_valid(self, form):
        orthomodeltype = form.save(commit=False)
        orthomodeltype.user = self.request.user
        return super(OrthoModelTypeCreate, self).form_valid(form)

class OrthoModelTypeUpdate(LoginRequiredMixin,UpdateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = OrthoModelType
    form = OrthoModelTypeForm
    template_name = 'orthomodoweb/orthomodeltype/orthomodeltype_form.html'
    fields=['code','name','description']   
    def get_queryset(self):
        base_qs = super(OrthoModelTypeUpdate, self).get_queryset()
        return base_qs.filter()

class OrthoModelTypeDelete(LoginRequiredMixin,DeleteView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = OrthoModelType
    template_name = 'orthomodoweb/orthomodeltype/orthomodeltype_confirm_delete.html'
    success_url = reverse_lazy('orthomodoweb:orthomodeltype-list')
    def get_queryset(self):
        base_qs = super(OrthoModelTypeDelete, self).get_queryset()
        return base_qs.filter()
    
        
#**************COLLECTION TYPE*****************
class CollectionTypeView(LoginRequiredMixin,generic.ListView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = CollectionType
    template_name = 'orthomodoweb/collectiontype/collectiontype_list.html'
    def get_queryset(self):
        """Return CollectionTypes for the logged-in user."""
        return CollectionType.objects.filter().order_by('name')  

class CollectionTypeCreate(LoginRequiredMixin,CreateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = CollectionType
    form = CollectionTypeForm
    template_name = 'orthomodoweb/collectiontype/collectiontype_add_form.html'
    fields=['code','name','description']   
    def form_valid(self, form):
        collectiontype = form.save(commit=False)
        collectiontype.user = self.request.user
        return super(CollectionTypeCreate, self).form_valid(form)

class CollectionTypeUpdate(LoginRequiredMixin,UpdateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = CollectionType
    form = CollectionTypeForm
    template_name = 'orthomodoweb/collectiontype/collectiontype_form.html'
    fields=['code','name','description']    
    def get_queryset(self):
        base_qs = super(CollectionTypeUpdate, self).get_queryset()
        return base_qs.filter()

class CollectionTypeDelete(LoginRequiredMixin,DeleteView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = CollectionType
    template_name = 'orthomodoweb/collectiontype/collectiontype_confirm_delete.html'
    success_url = reverse_lazy('orthomodoweb:collectiontype-list')
    def get_queryset(self):
        base_qs = super(CollectionTypeDelete, self).get_queryset()
        return base_qs.filter()
