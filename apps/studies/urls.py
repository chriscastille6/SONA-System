"""
URL patterns for studies app.
"""
from django.urls import path
from . import views

app_name = 'studies'

urlpatterns = [
    # Participant information document (full consent/info for psychological assessment platform)
    path('participant-information/', views.participant_information_consent, name='participant_information_consent'),
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
    
    # IRB AI Review
    path('<uuid:study_id>/irb-review/create/', views.irb_review_create, name='irb_review_create'),
    path('<uuid:study_id>/irb-review/<int:version>/', views.irb_review_detail, name='irb_review_detail'),
    path('<uuid:study_id>/irb-review/history/', views.irb_review_history, name='irb_review_history'),
    path('irb/dashboard/', views.irb_member_dashboard, name='irb_member_dashboard'),
    path('irb/assignments/<uuid:assignment_id>/toggle-email/', views.toggle_irb_email_updates, name='irb_toggle_email'),
    path('committee/', views.committee_dashboard, name='committee_dashboard'),
    
    # Protocol Submission
    path('<uuid:study_id>/protocol/enter/', views.protocol_enter, name='protocol_enter'),
    path('<uuid:study_id>/protocol/submit/', views.protocol_submit, name='protocol_submit'),
    path('protocol/submissions/', views.protocol_submission_list, name='protocol_submission_list'),
    path('protocol/submissions/<uuid:submission_id>/', views.protocol_submission_detail, name='protocol_submission_detail'),
    path('protocol/submissions/<uuid:submission_id>/college-rep-review/', views.protocol_college_rep_review, name='protocol_college_rep_review'),
    path('protocol/submissions/<uuid:submission_id>/assign-reviewers/', views.protocol_assign_reviewers, name='protocol_assign_reviewers'),
    path('protocol/submissions/<uuid:submission_id>/decision/', views.protocol_make_decision, name='protocol_make_decision'),
    path('protocol/submissions/<uuid:submission_id>/archive/', views.protocol_archive, name='protocol_archive'),
    path('protocol/submissions/<uuid:submission_id>/unarchive/', views.protocol_unarchive, name='protocol_unarchive'),

    # Protocol Amendments
    path('protocol/submissions/<uuid:submission_id>/amendments/', views.amendment_list, name='amendment_list'),
    path('protocol/submissions/<uuid:submission_id>/amendments/create/', views.amendment_create, name='amendment_create'),
    path('protocol/amendments/<uuid:amendment_id>/', views.amendment_detail, name='amendment_detail'),
    path('protocol/amendments/<uuid:amendment_id>/review/', views.amendment_review, name='amendment_review'),
]




