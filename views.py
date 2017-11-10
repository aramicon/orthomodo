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
from datetime import datetime, timedelta, time

from django.db import connections
from django.db.models import Count, Min, Sum, Avg, F, Q
from django.http import JsonResponse

from functools import reduce
import operator

import csv


from .models import Printer, Patient, Clinician, ModelType, LabItemType, CollectionType, OrthoModoJob, LabItem, LabItemMaterial

from orthomodoweb.forms import PrinterForm, PatientForm, ClinicianForm,LabItemTypeForm, CollectionTypeForm, OrthoModoJobForm, LabItemForm


#***************HOME PAGE***********
class HomeView(generic.TemplateView):
    template_name = 'orthomodoweb/home.html'
    def get_context_data(self, **kwargs):
        context=super(HomeView,self).get_context_data(**kwargs)
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, time())
        today_end = datetime.combine(tomorrow, time())
        #get jobs that have the selected date as the scan date (today)
        context['selected_day_jobs_scandate'] =  OrthoModoJob.objects.filter(scan_date__lte=today_end, scan_date__gte=today_start) 
        context['selected_day_jobs_printdate'] =  OrthoModoJob.objects.filter(print_date__lte=today_end, print_date__gte=today_start) 
        context['selected_day_jobs_plannedcollectiondate'] =  OrthoModoJob.objects.filter(planned_collection_date__lte=today_end, planned_collection_date__gte=today_start) 
        context['selected_day_jobs_dateupdated'] =  OrthoModoJob.objects.filter(date_updated__lte=today_end, date_updated__gte=today_start) 
        
       
        return context
    
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

        
        
def export_as_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orthomodo_export.csv"'

    writer = csv.writer(response,delimiter=',', quoting=csv.QUOTE_ALL, quotechar='"')
    writer.writerow(["patient.name", "patient.code", "clinician.name", "scan_date", "scan_date_entered_by", "scan_date_entered_when", "orthotrac_analysis_done", "orthotrac_analysis_notes", "printer", "is_stl_file_prepared", "stl_marked_as_prepared_by", "stl_marked_as_prepared_when", "is_printed", "print_date", "is_printed_marked_by", "is_printed_marked_when", "collection_type", "planned_collection_date", "planned_collection_time", "collection_notes", "is_collected", "is_collected_marked_by", "is_collected_marked_when", "flagged", "flag_status_set_by", "flag_status_set_when", "flag_status_note", "last_updated_by", "date_updated", "created_by", "date_created"])
    
    for omj in OrthoModoJob.objects.all():
        writer.writerow([omj.patient.name, omj.patient.code, omj.clinician.name, omj.scan_date, omj.scan_date_entered_by, omj.scan_date_entered_when, omj.orthotrac_analysis_done, omj.orthotrac_analysis_notes, omj.printer, omj.is_stl_file_prepared, omj.stl_marked_as_prepared_by, omj.stl_marked_as_prepared_when, omj.is_printed, omj.print_date, omj.is_printed_marked_by, omj.is_printed_marked_when, omj.collection_type, omj.planned_collection_date, omj.planned_collection_time, omj.collection_notes, omj.is_collected, omj.is_collected_marked_by, omj.is_collected_marked_when, omj.flagged, omj.flag_status_set_by, omj.flag_status_set_when, omj.flag_status_note, omj.last_updated_by, omj.date_updated, omj.created_by, omj.date_created])
   
    return response

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
        is_flagged_filter = self.request.GET.get('is_flagged')
        is_analysed_filter = self.request.GET.get('is_analysed')
        is_printed_filter = self.request.GET.get('is_printed')
        if query:
            query_list = query.split()
            print('Searching for ', file=sys.stderr)
            print('-'.join(query_list), file=sys.stderr)
            context['search_applied'] = '-'.join(query_list)
        if is_flagged_filter=='on':
            context['is_flagged_filter'] = '1'
        if is_analysed_filter=='on':
            context['is_analysed_filter'] = '1'
        if is_printed_filter=='on':
            context['is_printed_filter'] = '1'
        return context
    def get_queryset(self):
        """Return open OrthoModoJobs for the logged-in user."""
        print('Open jobs list', file=sys.stderr)
        result = OrthoModoJob.objects.filter(Q(flagged=True) | Q(is_collected=False)).order_by('-id') 
        query = self.request.GET.get('q')
        is_flagged_filter = self.request.GET.get('is_flagged')
        is_analysed_filter = self.request.GET.get('is_analysed')
        is_printed_filter = self.request.GET.get('is_printed')
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
                       (Q(collection_type__name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(planned_collection_date__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(collection_notes__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(flag_status_note__icontains=q) for q in query_list))
            )
        if is_flagged_filter=="on":
            result=result.filter(flagged=True)
        if is_analysed_filter=="on":
            result=result.filter(orthotrac_analysis_done=True)
        if is_printed_filter=="on":
            result=result.filter(is_printed=True)
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
        is_flagged_filter = self.request.GET.get('is_flagged')
        is_analysed_filter = self.request.GET.get('is_analysed')
        is_printed_filter = self.request.GET.get('is_printed')
        if query:
            query_list = query.split()
            print('Searching for ', file=sys.stderr)
            print('-'.join(query_list), file=sys.stderr)
            context['search_applied'] = '-'.join(query_list)
        if is_flagged_filter=='on':
            context['is_flagged_filter'] = '1'
        if is_analysed_filter=='on':
            context['is_analysed_filter'] = '1'
        if is_printed_filter=='on':
            context['is_printed_filter'] = '1'
        return context
    def get_queryset(self):
        """Return all OrthoModoJobs."""
        result = OrthoModoJob.objects.filter().order_by('-id') 
        query = self.request.GET.get('q')
        is_flagged_filter = self.request.GET.get('is_flagged')
        is_analysed_filter = self.request.GET.get('is_analysed')
        is_printed_filter = self.request.GET.get('is_printed')
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
                       (Q(collection_type__name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(planned_collection_date__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(collection_notes__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(flag_status_note__icontains=q) for q in query_list))
            )
        if is_flagged_filter=="on":
            result=result.filter(flagged=True)
        if is_analysed_filter=="on":
            result=result.filter(orthotrac_analysis_done=True)
        if is_printed_filter=="on":
            result=result.filter(is_printed=True)
        return result

class OrthoModoJobCreate(LoginRequiredMixin,CreateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = OrthoModoJob
    form = OrthoModoJobForm
    template_name = 'orthomodoweb/orthomodojob/orthomodojob_add_form.html'
    fields=['patient','clinician','scan_date','orthotrac_analysis_done','orthotrac_analysis_notes','printer','is_stl_file_prepared','is_printed','print_date','collection_type','planned_collection_date','planned_collection_time','collection_notes','is_collected','flagged','flag_status_note']   
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
    fields=['clinician','scan_date','model_type','orthotrac_analysis_done','orthotrac_analysis_notes','printer','is_stl_file_prepared','is_printed','print_date','is_poured','poured_date','collection_type','planned_collection_date','planned_collection_time','collection_notes','is_collected','flagged','flag_status_note']   
    def form_valid(self, form):
        print('save new job', file=sys.stderr)
        print(form.data['selected_patient_id'], file=sys.stderr)
        orthomodojob = form.save(commit=False)
        orthomodojob.user = self.request.user
        selected_patient_id = form.data['selected_patient_id']
        scan_date = form.data.get('scan_date',None)
        is_stl_file_prepared = form.data.get('is_stl_file_prepared',None)
        is_printed = form.data.get('is_printed',None)
        is_poured = form.data.get('is_poured',None)
        is_collected = form.data.get('is_collected',None)
        flagged = form.data.get('flagged',None)
        
        print('is_printed', file=sys.stderr)
        print(is_printed, file=sys.stderr)
        if (scan_date):
            orthomodojob.scan_date_entered_by =  self.request.user
            orthomodojob.scan_date_entered_when = timezone.now()
        if (is_stl_file_prepared):
            orthomodojob.stl_marked_as_prepared_by = self.request.user
            orthomodojob.stl_marked_as_prepared_when = timezone.now()
        if (is_printed):
            orthomodojob.is_printed_marked_by = self.request.user
            orthomodojob.is_printed_marked_when = timezone.now()
        if (is_poured):
            orthomodojob.is_poured_marked_by = self.request.user
            orthomodojob.is_poured_marked_when = timezone.now()
        if (is_collected):
            orthomodojob.is_collected_marked_by = self.request.user
            orthomodojob.is_collected_marked_when = timezone.now()
        if (flagged):
            orthomodojob.flag_status_set_by = self.request.user
            orthomodojob.flag_status_set_when = timezone.now()
        patient = get_object_or_404(Patient, id=selected_patient_id)
        orthomodojob.patient = patient
        orthomodojob.created_by = self.request.user
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
        context['model_type_list'] = ModelType.objects.all().order_by('id') 
        context['collection_type_list'] =  CollectionType.objects.all()
        return context

class OrthoModoJobUpdate(LoginRequiredMixin,UpdateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = OrthoModoJob
    form = OrthoModoJobForm
    template_name = 'orthomodoweb/orthomodojob/orthomodojob_form.html'
    fields=['patient','clinician','scan_date','model_type','orthotrac_analysis_done','orthotrac_analysis_notes','printer','is_stl_file_prepared','is_printed','print_date','is_poured','poured_date','collection_type','planned_collection_date','planned_collection_time','collection_notes','is_collected','flagged','flag_status_note']   
    def get_queryset(self):
        base_qs = super(OrthoModoJobUpdate, self).get_queryset()
        return base_qs.filter()
    def get_context_data(self, **kwargs):
        context=super(OrthoModoJobUpdate,self).get_context_data(**kwargs)
        context['patient_list'] =  Patient.objects.all()
        context['clinician_list'] =  Clinician.objects.all()
        context['printer_list'] =  Printer.objects.all()      
        context['collection_type_list'] =  CollectionType.objects.all()
        context['model_type_list'] = ModelType.objects.all().order_by('id') 
        #print(context['patient_list'], file=sys.stderr)      
        return context
    def form_invalid(self, form):
        print('save new job INVALID', file=sys.stderr)
        print(form.errors, file=sys.stderr)
        return HttpResponse("form is invalid... " + str(form.errors))
    def form_valid(self,form):
        print('update job', file=sys.stderr)
        orthomodojob_before_save = get_object_or_404(OrthoModoJob, id=self.kwargs['pk'])
        orthomodojob = form.save(commit=False)
        
        is_stl_file_prepared = form.data.get('is_stl_file_prepared',None)
            
        #print('existing scan_date', file=sys.stderr)
        #print(orthomodojob_before_save.scan_date, file=sys.stderr)
        #print('new value scan_date', file=sys.stderr)
        #print(orthomodojob.scan_date, file=sys.stderr)
        #update the user info if the settings have been added
        if (orthomodojob_before_save.scan_date == None and orthomodojob.scan_date != None):
            orthomodojob.scan_date_entered_by =  self.request.user
            orthomodojob.scan_date_entered_when = timezone.now()
        if (orthomodojob_before_save.is_stl_file_prepared == False and orthomodojob.is_stl_file_prepared == True):
            orthomodojob.stl_marked_as_prepared_by = self.request.user
            orthomodojob.stl_marked_as_prepared_when = timezone.now()
        if (orthomodojob_before_save.is_printed == False and orthomodojob.is_printed == True):
            orthomodojob.is_printed_marked_by = self.request.user
            orthomodojob.is_printed_marked_when = timezone.now()
        if (orthomodojob_before_save.is_poured == False and orthomodojob.is_poured == True):
            orthomodojob.is_poured_marked_by = self.request.user
            orthomodojob.is_poured_marked_when = timezone.now()
        if (orthomodojob_before_save.is_collected == False and orthomodojob.is_collected == True):
            orthomodojob.is_collected_marked_by = self.request.user
            orthomodojob.is_collected_marked_when = timezone.now()
        if (orthomodojob_before_save.flagged == False and orthomodojob.flagged == True):
            orthomodojob.flag_status_set_by = self.request.user
            orthomodojob.flag_status_set_when = timezone.now()
        orthomodojob.last_updated_by = self.request.user
        return super(OrthoModoJobUpdate, self).form_valid(form)

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
    def get_context_data(self, **kwargs):
        context=super(PrinterView,self).get_context_data(**kwargs)
        context['total_printers'] =  Printer.objects.filter().count() 
        return context

class PrinterCreate(LoginRequiredMixin,CreateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Printer
    form = PrinterForm
    template_name = 'orthomodoweb/printer/printer_add_form.html'
    fields=['name','code','description']   
    def form_valid(self, form):
        printer = form.save(commit=False)
        return super(PrinterCreate, self).form_valid(form)
    def form_invalid(self, form):
        return HttpResponse("form is invalid... " + str(form.errors))

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
    def form_invalid(self, form):
        return HttpResponse("form is invalid... " + str(form.errors))

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
    def get_context_data(self, **kwargs):
        context=super(PatientView,self).get_context_data(**kwargs)
        context['total_all_patients'] =  Patient.objects.filter().count() 
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            print('Searching for ', file=sys.stderr)
            print('-'.join(query_list), file=sys.stderr)
            context['search_applied'] = '-'.join(query_list)
        return context
    def get_queryset(self):
        """Return open Patients (can include search terms)"""
        result = Patient.objects.filter().order_by('name') 
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(code__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(reference_no__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(address__icontains=q) for q in query_list)) |    
                reduce(operator.and_,
                       (Q(email__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(phone_no_1__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(description__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(phone_no_2__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(dob__icontains=q) for q in query_list))
            )
        return result

class PatientCreate(LoginRequiredMixin,CreateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Patient
    form = PatientForm
    template_name = 'orthomodoweb/patient/patient_add_form.html'
    fields=['name','code','reference_no','email','phone_no_1','phone_no_2','address','dob','description'] 
    def form_invalid(self, form):
        return HttpResponse("form is invalid... " + str(form.errors))
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
    def form_invalid(self, form):
        return HttpResponse("form is invalid... " + str(form.errors))
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
    def get_context_data(self, **kwargs):
        context=super(ClinicianView,self).get_context_data(**kwargs)
        context['total_clinicians'] =  Clinician.objects.filter().count() 
        return context

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
    def form_invalid(self, form):
        return HttpResponse("form is invalid... " + str(form.errors))

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
    def form_invalid(self, form):
        return HttpResponse("form is invalid... " + str(form.errors))

class ClinicianDelete(LoginRequiredMixin,DeleteView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = Clinician
    template_name = 'orthomodoweb/clinician/clinician_confirm_delete.html'
    success_url = reverse_lazy('orthomodoweb:clinician-list')
    def get_queryset(self):
        base_qs = super(ClinicianDelete, self).get_queryset()
        return base_qs.filter()
        
#**************LabItemType*****************
class LabItemTypeView(LoginRequiredMixin,generic.ListView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = LabItemType
    template_name = 'orthomodoweb/labitemtype/labitemtype_list.html'
    def get_queryset(self):
        """Return LabItemTypes for the logged-in user."""
        return LabItemType.objects.filter().order_by('name')  
    def get_context_data(self, **kwargs):
        context=super(LabItemTypeView,self).get_context_data(**kwargs)
        context['total_labitemtypes'] =  LabItemType.objects.filter().count() 
        return context

class LabItemTypeCreate(LoginRequiredMixin,CreateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = LabItemType
    form = LabItemTypeForm
    template_name = 'orthomodoweb/labitemtype/labitemtype_add_form.html'
    fields=['code','name','description']   
    def form_valid(self, form):
        labitemtype = form.save(commit=False)
        labitemtype.user = self.request.user
        return super(LabItemTypeCreate, self).form_valid(form)
    def form_invalid(self, form):
        return HttpResponse("form is invalid... " + str(form.errors))

class LabItemTypeUpdate(LoginRequiredMixin,UpdateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = LabItemType
    form = LabItemTypeForm
    template_name = 'orthomodoweb/labitemtype/labitemtype_form.html'
    fields=['code','name','description']   
    def get_queryset(self):
        base_qs = super(LabItemTypeUpdate, self).get_queryset()
        return base_qs.filter()
    def form_invalid(self, form):
        return HttpResponse("form is invalid... " + str(form.errors))

class LabItemTypeDelete(LoginRequiredMixin,DeleteView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = LabItemType
    template_name = 'orthomodoweb/labitemtype/labitemtype_confirm_delete.html'
    success_url = reverse_lazy('orthomodoweb:labitemtype-list')
    def get_queryset(self):
        base_qs = super(LabItemTypeDelete, self).get_queryset()
        return base_qs.filter()
  
#**************LAB ITEM*****************
class LabItemCreate(LoginRequiredMixin,CreateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = LabItem
    form = LabItemForm
    template_name = 'orthomodoweb/labitem/labitem_add_form.html'
    fields=['lab_item_type','lab_item_material','is_blocked','is_made','made_date','notes']   
                    
    def form_valid(self, form):
        labitem = form.save(commit=False)  
        orthomodojob_id = form.data['orthomodojob_id']
        orthomodojob = get_object_or_404(OrthoModoJob, id=orthomodojob_id)        
        labitem.orthomodojob = orthomodojob
        return super(LabItemCreate, self).form_valid(form)
    def form_invalid(self, form):
        return HttpResponse("form is invalid... " + str(form.errors))
    def get_context_data(self, **kwargs):
        context=super(LabItemCreate,self).get_context_data(**kwargs)
        context['lab_item_type_list'] = LabItemType.objects.all().order_by('id')         
        context['lab_item_material_list'] = LabItemMaterial.objects.all().order_by('id') 
        context['j_id'] = self.kwargs['orthomodojob_id']
        return context

class LabItemUpdate(LoginRequiredMixin,UpdateView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = LabItem
    form = LabItemForm
    template_name = 'orthomodoweb/labitem/labitem_form.html'
    fields=['lab_item_type','lab_item_material','is_blocked','is_made','made_date','notes']    
    def get_context_data(self, **kwargs):
        context=super(LabItemUpdate,self).get_context_data(**kwargs)       
        context['lab_item_type_list'] = LabItemType.objects.all().order_by('id')         
        context['lab_item_material_list'] = LabItemMaterial.objects.all().order_by('id')         
        return context
    def get_queryset(self):
        base_qs = super(LabItemUpdate, self).get_queryset()
        return base_qs.filter()
    def form_invalid(self, form):
        return HttpResponse("form is invalid... " + str(form.errors))

class LabItemView(LoginRequiredMixin,generic.ListView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = LabItem
    template_name = 'orthomodoweb/labitem/labitem_list.html'
    def get_context_data(self, **kwargs):
        context=super(LabItemView,self).get_context_data(**kwargs)
        context['total_all_labitems'] =  LabItem.objects.filter().count() 
        query = self.request.GET.get('q')
        hide_made_items_filter = self.request.GET.get('hide_made_items')
        blocked_only_items_filter = self.request.GET.get('blocked_only_items')
        if query:
            query_list = query.split()
            #print('Searching for ', file=sys.stderr)
            #print('-'.join(query_list), file=sys.stderr)
            context['search_applied'] = '-'.join(query_list)
        if hide_made_items_filter=='on':
            context['hide_made_items_filter'] = '1'
        if blocked_only_items_filter=='on':
            context['blocked_only_items_filter'] = '1'
        return context
    def get_queryset(self):
        """Return open Patients (can include search terms)"""
        result = LabItem.objects.filter().order_by('-id') 
        query = self.request.GET.get('q')
        hide_made_items_filter = self.request.GET.get('hide_made_items')
        blocked_only_items_filter = self.request.GET.get('blocked_only_items')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(made_date__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(notes__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(orthomodojob__patient__name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(lab_item_type__name__icontains=q) for q in query_list)) |    
                reduce(operator.and_,
                       (Q(lab_item_material__name__icontains=q) for q in query_list))              
            )
        if hide_made_items_filter:           
            result = result.filter(is_made=False)          
        if blocked_only_items_filter=='on':
            result = result.filter(is_blocked=True)
        return result
        
#**************COLLECTION TYPE*****************
class CollectionTypeView(LoginRequiredMixin,generic.ListView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = CollectionType
    template_name = 'orthomodoweb/collectiontype/collectiontype_list.html'
    def get_queryset(self):
        """Return CollectionTypes for the logged-in user."""
        return CollectionType.objects.filter().order_by('name')  
    def get_context_data(self, **kwargs):
        context=super(CollectionTypeView,self).get_context_data(**kwargs)
        context['total_collectiontypes'] =  CollectionType.objects.filter().count() 
        return context

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
    def form_invalid(self, form):
        return HttpResponse("form is invalid... " + str(form.errors))

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
    def form_invalid(self, form):
        return HttpResponse("form is invalid... " + str(form.errors))

class CollectionTypeDelete(LoginRequiredMixin,DeleteView):
    login_url = 'orthomodoweb:login'
    redirect_field_name = 'orthomodoweb:home'
    model = CollectionType
    template_name = 'orthomodoweb/collectiontype/collectiontype_confirm_delete.html'
    success_url = reverse_lazy('orthomodoweb:collectiontype-list')
    def get_queryset(self):
        base_qs = super(CollectionTypeDelete, self).get_queryset()
        return base_qs.filter()
