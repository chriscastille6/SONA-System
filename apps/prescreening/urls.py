"""
URL patterns for prescreening app.
"""
from django.urls import path
from . import views

app_name = 'prescreening'

urlpatterns = [
    path('', views.prescreen_form, name='form'),
    path('submit/', views.submit_prescreen, name='submit'),
]




