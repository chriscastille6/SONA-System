"""
URL patterns for credits app.
"""
from django.urls import path
from . import views

app_name = 'credits'

urlpatterns = [
    path('my-credits/', views.my_credits, name='my_credits'),
    path('grant/', views.grant_credits, name='grant'),
]




