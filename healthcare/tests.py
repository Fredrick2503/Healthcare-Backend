import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from healthcare.models import Patient, Doctor, PatientDoctorMapping

User = get_user_model()

class HealthcareModelTests(TestCase):
    """
    Unit tests for Patient, Doctor, and PatientDoctorMapping database models.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='doctor_admin@hospital.com',
            name='Hospital Admin',
            password='AdminPassword123!'
        )

        self.patient = Patient.objects.create(
            created_by=self.user,
            name='John Doe',
            email='johndoe@example.com',
            phone='+1234567890',
            date_of_birth=datetime.date(1990, 5, 15),
            gender='Male',
            address='123 Maple Street, Cityville'
        )

        self.doctor = Doctor.objects.create(
            created_by=self.user,
            name='Gregory House',
            email='house@ppth.org',
            phone='+1987654321',
            specialization='Diagnostic Medicine',
            license_number='MED-99882',
            address='Princeton-Plainsboro Hospital'
        )

    def test_patient_creation(self):
        self.assertEqual(self.patient.name, 'John Doe')
        self.assertEqual(self.patient.created_by, self.user)
        self.assertIsNotNone(self.patient.created_at)
        self.assertIsNotNone(self.patient.updated_at)
        self.assertIn('John Doe', str(self.patient))

    def test_doctor_creation(self):
        self.assertEqual(self.doctor.name, 'Gregory House')
        self.assertEqual(self.doctor.specialization, 'Diagnostic Medicine')
        self.assertEqual(self.doctor.created_by, self.user)
        self.assertIsNotNone(self.doctor.created_at)
        self.assertIsNotNone(self.doctor.updated_at)
        self.assertIn('House', str(self.doctor))

    def test_patient_doctor_mapping_creation(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            assigned_by=self.user
        )
        self.assertEqual(mapping.patient, self.patient)
        self.assertEqual(mapping.doctor, self.doctor)
        self.assertEqual(mapping.assigned_by, self.user)
        self.assertIsNotNone(mapping.assigned_at)
        self.assertIn(self.patient.name, str(mapping))

    def test_unique_patient_doctor_mapping(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            assigned_by=self.user
        )
        # Attempting to assign the same doctor to the same patient must violate unique_together
        with self.assertRaises(IntegrityError):
            PatientDoctorMapping.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                assigned_by=self.user
            )
