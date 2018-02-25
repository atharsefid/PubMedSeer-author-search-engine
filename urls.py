from django.conf.urls.defaults import patterns, include, url
from django.views.generic import RedirectView
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
#import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
     #url(r'^rsc/', include('rsc.urls', namespace="rsc")),
     url(r'^transfer_to_advance',  'rsc.views.transfer_to_advance'),
     url(r'^viewdocument/transfer_to_advance',  'rsc.views.transfer_to_advance'),
     url(r'^export_papers',  'rsc.views.export_papers'),
     url(r'^export_author_info',  'rsc.views.export_author_info'),
     url(r'^export_results_papers',  'rsc.views.export_results_papers'),
     url(r'^export_results',  'rsc.views.export_results'),
     url(r'^advance_export_results_papers',  'rsc.views.advanced_export_results_papers'),
     url(r'^advance_export_results',  'rsc.views.advanced_export_results'),
     url(r'^advanced_search',  'rsc.views.advanced_search'),
     #url(r'^transfer_to_record',  'rsc.views.transfer_to_record'),
     url(r'^record_search', 'rsc.views.record_search'),
     url(r'^$', 'rsc.views.home'),
     url(r'^viewdocument/', 'rsc.views.viewdocument'),
     #url(r'^download/(?P<loc>.+)/$', 'rsc.views.download'),
     #url(r'^download/(?P<loc>~[^0-9A-Za-z\\/]~)/$', 'rsc.views.download'),
     # Uncomment the admin/doc line below to enable admin documentation:
     # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

     # Uncomment the next line to enable the admin:
)


