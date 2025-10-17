"""
URL patterns for studies app.
"""
from django.urls import path
from . import views

app_name = 'studies'

urlpatterns = [
    # Browse studies
    path('', views.study_list, name='list'),
    path('<uuid:pk>/', views.study_detail, name='detail'),
    
    # Timeslot booking
    path('timeslot/<uuid:pk>/book/', views.book_timeslot, name='book_timeslot'),
    path('signup/<uuid:pk>/cancel/', views.cancel_signup, name='cancel_signup'),
    
    # My bookings (participant)
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    
    # Researcher views
    path('researcher/', views.researcher_dashboard, name='researcher_dashboard'),
    path('researcher/create/', views.create_study, name='create'),
    path('researcher/<uuid:pk>/edit/', views.edit_study, name='edit'),
    path('researcher/<uuid:pk>/timeslots/', views.manage_timeslots, name='manage_timeslots'),
    path('researcher/<uuid:pk>/roster/', views.study_roster, name='roster'),
    path('researcher/signup/<uuid:pk>/attendance/', views.mark_attendance, name='mark_attendance'),
    
    # Protocol and data collection
    path('<slug:slug>/run/', views.run_protocol, name='run_protocol'),
    path('<slug:slug>/status/', views.study_status, name='status'),
]




