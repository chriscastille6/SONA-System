"""
URL patterns for reporting app.
"""
from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('', views.reports_home, name='home'),
    path('course/<uuid:course_id>/credits.csv', views.course_credits_csv, name='course_credits_csv'),
    path('study/<uuid:study_id>/', views.study_report, name='study_report'),
]




