from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from . import views

app_name='orthomodoweb'

urlpatterns = [
    #home page
    url(r'^$',views.HomeView.as_view(),name='home'),
    
    #About/Help page
    url(r'^guide/$',views.UserGuide.as_view(),name='userguide'),    
       
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
    
    #labitemtypes
    url(r'^labitemtype/$', views.LabItemTypeView.as_view(), name='labitemtype-list'),
    url(r'^labitemtype/add/$', views.LabItemTypeCreate.as_view(), name='labitemtype-add'),
    url(r'^labitemtype/(?P<pk>[0-9]+)/$', views.LabItemTypeUpdate.as_view(), name='labitemtype-update'),
    url(r'^labitemtype/(?P<pk>[0-9]+)/delete$', views.LabItemTypeDelete.as_view(), name='labitemtype-delete'),
    
     #collectiontype
    url(r'^collectiontype/$', views.CollectionTypeView.as_view(), name='collectiontype-list'),
    url(r'^collectiontype/add/$', views.CollectionTypeCreate.as_view(), name='collectiontype-add'),
    url(r'^collectiontype/(?P<pk>[0-9]+)/$', views.CollectionTypeUpdate.as_view(), name='collectiontype-update'),
    url(r'^collectiontype/(?P<pk>[0-9]+)/delete$', views.CollectionTypeDelete.as_view(), name='collectiontype-delete'),
    
    #labitems
     url(r'^(?P<orthomodojob_id>[0-9]+)/labitem/add/$', views.LabItemCreate.as_view(), name='labitem-create'),
     url(r'^(?P<orthomodojob_id>[0-9]+)/labitem/(?P<pk>[0-9]+)/$', views.LabItemUpdate.as_view(), name='labitem-update'),
     url(r'^orthomodojob/labitem/$', views.LabItemView.as_view(), name='labitem-list'),
     
     #redirect everything unknown to the home pahe
     #url(r'^.*$', RedirectView.as_view(pattern_name='home', permanent=False), name='index')
]