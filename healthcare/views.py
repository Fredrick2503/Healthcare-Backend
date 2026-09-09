from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from healthcare.models import Patient, Doctor, PatientDoctorMapping
from healthcare.serializers import (
    PatientSerializer,
    DoctorSerializer,
    PatientDoctorMappingSerializer,
)

class PatientViewSet(viewsets.ModelViewSet):
    """
    Patient Management APIs:
    - POST /api/patients/ : Add a new patient (Authenticated users only)
    - GET /api/patients/ : Retrieve all patients created by the authenticated user
    - GET /api/patients/<id>/ : Get details of a specific patient
    - PUT /api/patients/<id>/ : Update patient details
    - DELETE /api/patients/<id>/ : Delete a patient record
    """
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retrieve all patients created by the authenticated user
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class DoctorViewSet(viewsets.ModelViewSet):
    """
    Doctor Management APIs:
    - POST /api/doctors/ : Add a new doctor (Authenticated users only)
    - GET /api/doctors/ : Retrieve all doctors
    - GET /api/doctors/<id>/ : Get details of a specific doctor
    - PUT /api/doctors/<id>/ : Update doctor details
    - DELETE /api/doctors/<id>/ : Delete a doctor record
    """
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    queryset = Doctor.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class PatientDoctorMappingListCreateView(generics.ListCreateAPIView):
    """
    Patient-Doctor Mapping APIs:
    - POST /api/mappings/ : Assign a doctor to a patient
    - GET /api/mappings/ : Retrieve all patient-doctor mappings
    """
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [IsAuthenticated]
    queryset = PatientDoctorMapping.objects.all().select_related('patient', 'doctor', 'assigned_by')

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

class PatientDoctorMappingDetailView(APIView):
    """
    Patient-Doctor Mapping APIs:
    - GET /api/mappings/<patient_id>/ : Get all doctors assigned to a specific patient
    - DELETE /api/mappings/<id>/ : Remove a doctor from a patient (delete mapping by ID)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Get all doctors assigned to a specific patient (patient_id = pk).
        """
        patient = get_object_or_404(Patient, pk=pk)
        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('patient', 'doctor', 'assigned_by')
        serializer = PatientDoctorMappingSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Remove a doctor from a patient by mapping ID.
        """
        mapping = get_object_or_404(PatientDoctorMapping, pk=pk)
        mapping.delete()
        return Response(
            {"message": "Patient-doctor mapping removed successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
