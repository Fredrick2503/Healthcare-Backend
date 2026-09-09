from django.urls import path, include
from rest_framework.routers import DefaultRouter

from healthcare.views import (
    PatientViewSet,
    DoctorViewSet,
    PatientDoctorMappingListCreateView,
    PatientDoctorMappingDetailView,
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'doctors', DoctorViewSet, basename='doctor')

urlpatterns = [
    # Router routes for Patients and Doctors
    path('', include(router.urls)),

    # Patient-Doctor Mapping routes
    path('mappings/', PatientDoctorMappingListCreateView.as_view(), name='mapping_list_create'),
    path('mappings/<int:pk>/', PatientDoctorMappingDetailView.as_view(), name='mapping_detail'),
]
