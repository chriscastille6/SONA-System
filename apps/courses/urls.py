"""
URL patterns for courses app.
"""
from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('<uuid:pk>/', views.course_detail, name='detail'),
    path('my-courses/', views.my_courses, name='my_courses'),
]




