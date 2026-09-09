from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse, OpenApiExample

from healthcare.models import Patient, Doctor, PatientDoctorMapping
from healthcare.serializers import (
    PatientSerializer,
    DoctorSerializer,
    PatientDoctorMappingSerializer,
)

@extend_schema_view(
    list=extend_schema(
        tags=['Patients'],
        summary="List User's Patients",
        description="Retrieve all patient records created by the currently authenticated user."
    ),
    create=extend_schema(
        tags=['Patients'],
        summary="Create Patient",
        description="Add a new patient record. The created_by attribute is automatically assigned to the authenticated user.",
        examples=[
            OpenApiExample(
                "New Patient Example",
                value={
                    "name": "Alice Johnson",
                    "email": "alice.johnson@example.com",
                    "phone": "+1-555-200-001",
                    "date_of_birth": "1992-04-18",
                    "gender": "Female",
                    "address": "742 Evergreen Terrace, Springfield, OR"
                },
                request_only=True
            )
        ]
    ),
    retrieve=extend_schema(
        tags=['Patients'],
        summary="Get Patient Details",
        description="Retrieve full details for a specific patient by ID."
    ),
    update=extend_schema(
        tags=['Patients'],
        summary="Update Patient (Full)",
        description="Replace all details of an existing patient record."
    ),
    partial_update=extend_schema(
        tags=['Patients'],
        summary="Update Patient (Partial)",
        description="Update specific fields of an existing patient record."
    ),
    destroy=extend_schema(
        tags=['Patients'],
        summary="Delete Patient",
        description="Permanently delete a patient record and any associated mappings."
    )
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
    queryset = Patient.objects.all()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Patient.objects.none()
        # Retrieve all patients created by the authenticated user
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

@extend_schema_view(
    list=extend_schema(
        tags=['Doctors'],
        summary="List All Doctors",
        description="Retrieve all registered medical practitioners across the platform."
    ),
    create=extend_schema(
        tags=['Doctors'],
        summary="Create Doctor",
        description="Register a new doctor record with specialization and medical license number.",
        examples=[
            OpenApiExample(
                "New Doctor Example",
                value={
                    "name": "Gregory House",
                    "email": "house@ppth.org",
                    "phone": "+1-555-010-001",
                    "specialization": "Diagnostic Medicine",
                    "license_number": "LIC-99882",
                    "address": "Princeton-Plainsboro Hospital, NJ"
                },
                request_only=True
            )
        ]
    ),
    retrieve=extend_schema(
        tags=['Doctors'],
        summary="Get Doctor Details",
        description="Retrieve full details for a specific doctor by ID."
    ),
    update=extend_schema(
        tags=['Doctors'],
        summary="Update Doctor (Full)",
        description="Replace all fields of an existing doctor record."
    ),
    partial_update=extend_schema(
        tags=['Doctors'],
        summary="Update Doctor (Partial)",
        description="Update specific fields of an existing doctor record."
    ),
    destroy=extend_schema(
        tags=['Doctors'],
        summary="Delete Doctor",
        description="Permanently delete a doctor record."
    )
)
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

    @extend_schema(
        tags=['Mappings'],
        summary="List All Patient-Doctor Mappings",
        description="Retrieve all assignments between patients and doctors, with full nested doctor and patient information."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Mappings'],
        summary="Assign Doctor to Patient",
        description="Create an assignment mapping between a patient and a doctor. Validates against duplicate assignments.",
        request=PatientDoctorMappingSerializer,
        responses={
            201: PatientDoctorMappingSerializer,
            400: OpenApiResponse(description="Doctor is already assigned to this patient.")
        },
        examples=[
            OpenApiExample(
                "Assign Doctor Example",
                value={
                    "patient_id": 1,
                    "doctor_id": 1
                },
                request_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

class PatientDoctorMappingDetailView(APIView):
    """
    Patient-Doctor Mapping APIs:
    - GET /api/mappings/<patient_id>/ : Get all doctors assigned to a specific patient
    - DELETE /api/mappings/<id>/ : Remove a doctor from a patient (delete mapping by ID)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PatientDoctorMappingSerializer

    @extend_schema(
        tags=['Mappings'],
        operation_id='mappings_get_doctors_by_patient',
        summary="Get Doctors Assigned to a Specific Patient",
        description="Retrieves the list of all doctors assigned to the specified patient ID.",
        parameters=[
            OpenApiParameter(
                name='pk',
                description='ID of the Patient whose assigned doctors to retrieve',
                required=True,
                type=int,
                location=OpenApiParameter.PATH
            )
        ],
        responses={
            200: PatientDoctorMappingSerializer(many=True),
            404: OpenApiResponse(description="Patient with the specified ID was not found.")
        }
    )
    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('patient', 'doctor', 'assigned_by')
        serializer = PatientDoctorMappingSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Mappings'],
        operation_id='mappings_delete_assignment',
        summary="Remove Doctor from Patient (Delete Mapping)",
        description="Deletes a patient-doctor assignment by its mapping record ID.",
        parameters=[
            OpenApiParameter(
                name='pk',
                description='ID of the Mapping record to remove',
                required=True,
                type=int,
                location=OpenApiParameter.PATH
            )
        ],
        responses={
            204: OpenApiResponse(description="Patient-doctor mapping removed successfully."),
            404: OpenApiResponse(description="Mapping record with specified ID not found.")
        }
    )
    def delete(self, request, pk):
        mapping = get_object_or_404(PatientDoctorMapping, pk=pk)
        mapping.delete()
        return Response(
            {"message": "Patient-doctor mapping removed successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
