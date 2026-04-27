from django.urls import path
from . import views

app_name = 'prams'

urlpatterns = [
    path('studies/', views.study_list, name='study_list'),
    path('studies/<uuid:study_id>/ical/', views.study_ical, name='study_ical'),
    path('signup/', views.SignupView.as_view(), name='signup'),
]
