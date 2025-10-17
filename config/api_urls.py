"""
API URL router.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.studies import views as study_views

router = DefaultRouter()

# Import and register viewsets here when created
# from apps.studies.api import StudyViewSet
# router.register(r'studies', StudyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    
    # Protocol response submission
    path('studies/<uuid:study_id>/submit/', study_views.submit_response, name='submit_response'),
]




