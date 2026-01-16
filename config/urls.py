"""
URL Configuration for Research Participant Recruitment System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Home (must be first to avoid conflicts)
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Apps
    path('accounts/', include('apps.accounts.urls')),
    path('studies/', include('apps.studies.urls')),
    path('prescreening/', include('apps.prescreening.urls')),
    path('credits/', include('apps.credits.urls')),
    path('courses/', include('apps.courses.urls')),
    path('reports/', include('apps.reporting.urls')),
    
    # API
    path('api/', include('config.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "PRAMS Administration"
admin.site.site_title = "PRAMS"
admin.site.index_title = "Participant Recruitment & Management System"

