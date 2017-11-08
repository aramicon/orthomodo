from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from . import views

app_name='orthomodoweb'

urlpatterns = [
    #home page
    url(r'^home/$',views.HomeView.as_view(),name='home'),
	
	#export
	url(r'^export_as_csv/$',views.export_as_csv,name='export_as_csv'),
    
    #orthomodojob
    url(r'^orthomodojob/open/$', views.OrthoModoJobViewOpen.as_view(), name='orthomodojob-open-list'),
    url(r'^orthomodojob/all/$', views.OrthoModoJobViewAll.as_view(), name='orthomodojob-all-list'),
    url(r'^orthomodojob/add/$', views.OrthoModoJobCreate.as_view(), name='orthomodojob-add'),
    url(r'^orthomodojob/(?P<pk>[0-9]+)/$', views.OrthoModoJobUpdate.as_view(), name='orthomodojob-update'),
    url(r'^orthomodojob/(?P<pk>[0-9]+)/delete$', views.OrthoModoJobDelete.as_view(), name='orthomodojob-delete'),
       
    #login/logout/signup
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'orthomodoweb:home'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^admin/', admin.site.urls),
    
    #printers
    url(r'^printer/$', views.PrinterView.as_view(), name='printer-list'),
    url(r'^printer/add/$', views.PrinterCreate.as_view(), name='printer-add'),
    url(r'^printer/(?P<pk>[0-9]+)/$', views.PrinterUpdate.as_view(), name='printer-update'),
    url(r'^printer/(?P<pk>[0-9]+)/delete$', views.PrinterDelete.as_view(), name='printer-delete'),
    
    #patients
    url(r'^patient/$', views.PatientView.as_view(), name='patient-list'),
    url(r'^patient/add/$', views.PatientCreate.as_view(), name='patient-add'),
    url(r'^patient/(?P<pk>[0-9]+)/$', views.PatientUpdate.as_view(), name='patient-update'),
    url(r'^patient/(?P<pk>[0-9]+)/delete$', views.PatientDelete.as_view(), name='patient-delete'),
    url(r'^patient/(?P<patient_id>[0-9]+)/addjob$', views.OrthoModoPatientJobCreate.as_view(), name='patient-add-job'),
    
    #clinicians
    url(r'^clinician/$', views.ClinicianView.as_view(), name='clinician-list'),
    url(r'^clinician/add/$', views.ClinicianCreate.as_view(), name='clinician-add'),
    url(r'^clinician/(?P<pk>[0-9]+)/$', views.ClinicianUpdate.as_view(), name='clinician-update'),
    url(r'^clinician/(?P<pk>[0-9]+)/delete$', views.ClinicianDelete.as_view(), name='clinician-delete'),
    
    #orthomodeltypes
    url(r'^orthomodeltype/$', views.OrthoModelTypeView.as_view(), name='orthomodeltype-list'),
    url(r'^orthomodeltype/add/$', views.OrthoModelTypeCreate.as_view(), name='orthomodeltype-add'),
    url(r'^orthomodeltype/(?P<pk>[0-9]+)/$', views.OrthoModelTypeUpdate.as_view(), name='orthomodeltype-update'),
    url(r'^orthomodeltype/(?P<pk>[0-9]+)/delete$', views.OrthoModelTypeDelete.as_view(), name='orthomodeltype-delete'),
    
     #collectiontype
    url(r'^collectiontype/$', views.CollectionTypeView.as_view(), name='collectiontype-list'),
    url(r'^collectiontype/add/$', views.CollectionTypeCreate.as_view(), name='collectiontype-add'),
    url(r'^collectiontype/(?P<pk>[0-9]+)/$', views.CollectionTypeUpdate.as_view(), name='collectiontype-update'),
    url(r'^collectiontype/(?P<pk>[0-9]+)/delete$', views.CollectionTypeDelete.as_view(), name='collectiontype-delete'),
]