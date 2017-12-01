from django.db import models
from django.urls import reverse
from django.conf import settings

class Printer(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    date_updated = models.DateTimeField('Date updated',auto_now=True)
    date_created = models.DateTimeField('Date Created',auto_now_add=True)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
       return reverse('orthomodoweb:printer-update', kwargs={'pk': self.pk})

class Patient(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20,unique=True)
    reference_no = models.CharField(max_length=50,blank=True)
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone_no_1 = models.CharField(blank=True,max_length=50)
    phone_no_2 = models.CharField(blank=True,max_length=50)
    address = models.CharField(blank=True,max_length=300)
    dob = models.DateField(blank=True, null=True)
    date_updated = models.DateTimeField('Date updated',auto_now=True)
    date_created = models.DateTimeField('Date Created',auto_now_add=True)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
       return reverse('orthomodoweb:patient-update', kwargs={'pk': self.pk})
       
class Clinician(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20,unique=True)
    description = models.TextField(blank=True)
    date_updated = models.DateTimeField('Date updated',auto_now=True)
    date_created = models.DateTimeField('Date Created',auto_now_add=True)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
       return reverse('orthomodoweb:clinician-update', kwargs={'pk': self.pk})
       
class LabItemType(models.Model):
    code = models.CharField(max_length=20,unique=True)
    name = models.CharField(max_length=200)    
    description = models.TextField(blank=True)
    date_updated = models.DateTimeField('Date updated',auto_now=True)
    date_created = models.DateTimeField('Date Created',auto_now_add=True)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
       return reverse('orthomodoweb:labitemtype-update', kwargs={'pk': self.pk})

class LabItemMaterial(models.Model):
    code = models.CharField(max_length=20,unique=True)
    name = models.CharField(max_length=200)    
    description = models.TextField(blank=True)
    date_updated = models.DateTimeField('Date updated',auto_now=True)
    date_created = models.DateTimeField('Date Created',auto_now_add=True)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
       return reverse('orthomodoweb:labitemmaterial-update', kwargs={'pk': self.pk})
       
       
class CollectionType(models.Model):    
    code = models.CharField(max_length=20,unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_updated = models.DateTimeField('Date updated',auto_now=True)
    date_created = models.DateTimeField('Date Created',auto_now_add=True)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
       return reverse('orthomodoweb:collectiontype-update', kwargs={'pk': self.pk})

class ModelType(models.Model):     
    name = models.CharField(max_length=30, unique=True)
    def __str__(self):
        return self.name
        
class CreatedModelUse(models.Model):     
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
 
class OrthoModoJob(models.Model):      
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    clinician = models.ForeignKey(Clinician, on_delete=models.PROTECT)
    model_type = models.ForeignKey(ModelType, on_delete=models.PROTECT)
    scan_date = models.DateField(blank=True, null=True)    
    scan_date_entered_by = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True,related_name="orthomodojob_scan_date_entered_by")
    scan_date_entered_when = models.DateTimeField(blank=True, null=True)    
    orthotrac_analysis_done = models.BooleanField(default=False)
    orthotrac_analysis_notes = models.TextField(blank=True)    
    printer = models.ForeignKey(Printer, on_delete=models.PROTECT,blank=True,null=True)
    is_stl_file_prepared = models.BooleanField(default=False)
    stl_marked_as_prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True,related_name="orthomodojob_stl_marked_as_prepared_by")
    stl_marked_as_prepared_when = models.DateTimeField(blank=True, null=True)    
    is_printed = models.BooleanField(default=False)
    print_date = models.DateField(blank=True, null=True)   
    is_printed_marked_by = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True,related_name="orthomodojob_is_printed_marked_by")
    is_printed_marked_when = models.DateTimeField(blank=True, null=True)  
    is_poured =  models.BooleanField(default=False)
    poured_date = models.DateField(blank=True, null=True)   
    is_poured_marked_by = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True,related_name="orthomodojob_is_poured_marked_by")
    is_poured_marked_when = models.DateTimeField(blank=True, null=True) 
    created_model_use = models.ForeignKey(CreatedModelUse, on_delete=models.PROTECT,blank=True,null=True)    
    collection_type = models.ForeignKey(CollectionType, on_delete=models.PROTECT,blank=True,null=True)
    planned_collection_date = models.DateField(blank=True, null=True)    
    planned_collection_time = models.TimeField(blank=True, null=True)
    collection_notes = models.TextField(blank=True)    
    is_collected = models.BooleanField(default=False)
    is_collected_marked_by = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True,related_name="orthomodojob_is_collected_marked_by")
    is_collected_marked_when = models.DateTimeField(blank=True, null=True)    
    flagged = models.BooleanField(default=False)
    flag_status_set_by = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True,related_name="orthomodojob_flag_status_set_by")
    flag_status_set_when = models.DateTimeField(blank=True, null=True)
    flag_status_note = models.TextField(blank=True)
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True,related_name="orthomodojob_last_updated_by")
    date_updated = models.DateTimeField('Date updated',auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True,related_name="orthomodojob_created_by")
    date_created = models.DateTimeField('Date Created',auto_now_add=True)
    def __str__(self):
        return str(self.id)
    def get_absolute_url(self):
       return reverse('orthomodoweb:orthomodojob-update', kwargs={'pk': self.pk})
   
class LabItem(models.Model):
    orthomodojob = models.ForeignKey(OrthoModoJob, on_delete=models.PROTECT)
    lab_item_type = models.ForeignKey(LabItemType, on_delete=models.PROTECT)
    lab_item_material = models.ForeignKey(LabItemMaterial, on_delete=models.PROTECT)
    is_blocked =  models.BooleanField(default=False)
    is_made =  models.BooleanField(default=False)
    made_date = models.DateTimeField(blank=True, null=True)  
    is_made_marked_by = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True,related_name="lab_item_is_made_marked_by")
    is_made_marked_when = models.DateTimeField(blank=True, null=True)     
    notes= models.TextField(blank=True)
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True,related_name="lab_item_last_updated_by")
    date_updated = models.DateTimeField('Date updated',auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True,related_name="lab_item_created_by")
    date_created = models.DateTimeField('Date Created',auto_now_add=True)
    def __str__(self):
        return self.lab_item_type.name
    def get_absolute_url(self):
       return reverse('orthomodoweb:orthomodojob-update', kwargs={'pk': self.orthomodojob.id})