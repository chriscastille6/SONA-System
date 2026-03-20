"""
URL patterns for studies app.
"""
from django.urls import path
from . import views

app_name = 'studies'

urlpatterns = [
    # Participant information document (full consent/info for psychological assessment platform)
    path('participant-information/', views.participant_information_consent, name='participant_information_consent'),
    path('irb-standards/', views.social_science_irb_standards, name='social_science_irb_standards'),
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
    
    # EXT-AM4 PRAMS summary (both paths; use extam4-summary if docs/ returns 404)
    path('extam4-summary/', views.extam4_summary_html, name='extam4_summary'),
    path('docs/extam4-summary/', views.extam4_summary_html, name='extam4_summary_docs'),
    # Protocol and data collection
    # Hosted live survey (goals-refs Wave 1) — before slug routes
    path('goals-refs/survey/', views.goals_refs_live_survey, name='goals_refs_live_survey'),
    path('<slug:slug>/run/', views.run_protocol, name='run_protocol'),
    path('<slug:slug>/protocol/preview/', views.protocol_preview, name='protocol_preview'),
    path('<slug:slug>/protocol/vignettes/', views.protocol_vignettes, name='protocol_vignettes'),
    path('<slug:slug>/protocol/documentation/', views.protocol_study_documentation, name='protocol_study_documentation'),
    path('<slug:slug>/protocol/consent/', views.protocol_consent, name='protocol_consent'),
    path('<slug:slug>/protocol/consent/done/', views.protocol_consent_done, name='protocol_consent_done'),
    # HR SJT student secondary-data consent (MNGT 425)
    path('hr-sjt/student-data-consent/', views.hr_sjt_student_data_consent, name='hr_sjt_student_data_consent'),
    path('hr-sjt/student-data-consent/done/', views.hr_sjt_student_data_consent_done, name='hr_sjt_student_data_consent_done'),
    path('hr-sjt/professional-consent/', views.hr_sjt_professional_consent, name='hr_sjt_professional_consent'),
    path('hr-sjt/professional-demographics/', views.hr_sjt_professional_demographics, name='hr_sjt_professional_demographics'),
    path('hr-sjt/infographic/', views.hr_sjt_infographic_signup, name='hr_sjt_infographic_signup'),
    path('hr-sjt/infographic/preview/', views.hr_sjt_infographic_preview, name='hr_sjt_infographic_preview'),
    path('hr-sjt/infographic/image/', views.hr_sjt_infographic_image, name='hr_sjt_infographic_image'),
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




