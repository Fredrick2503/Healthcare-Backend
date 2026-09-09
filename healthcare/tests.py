import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from healthcare.models import Patient, Doctor, PatientDoctorMapping

User = get_user_model()

class HealthcareModelTests(TestCase):
    """
    Unit tests for database models.
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
        with self.assertRaises(IntegrityError):
            PatientDoctorMapping.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                assigned_by=self.user
            )

class HealthcareAPITests(APITestCase):
    """
    Comprehensive unit tests for Patient, Doctor, and Mapping REST APIs.
    """

    def setUp(self):
        # User A
        self.user_a = User.objects.create_user(
            email='usera@example.com',
            name='User Alpha',
            password='Password123!'
        )
        # User B
        self.user_b = User.objects.create_user(
            email='userb@example.com',
            name='User Beta',
            password='Password123!'
        )

        # Pre-populate patient for User A
        self.patient_a = Patient.objects.create(
            created_by=self.user_a,
            name='Patient Alpha One',
            email='p_alpha@example.com',
            phone='1112223333',
            date_of_birth=datetime.date(1985, 1, 1),
            gender='Female',
            address='100 First Ave'
        )

        # Pre-populate patient for User B
        self.patient_b = Patient.objects.create(
            created_by=self.user_b,
            name='Patient Beta One',
            email='p_beta@example.com',
            phone='4445556666',
            date_of_birth=datetime.date(1992, 2, 2),
            gender='Male',
            address='200 Second Ave'
        )

        # Pre-populate doctors
        self.doctor_one = Doctor.objects.create(
            created_by=self.user_a,
            name='Doctor Strange',
            email='strange@marvel.com',
            phone='5551234567',
            specialization='Neuro Surgery',
            license_number='DOC-001',
            address='177A Bleecker St'
        )

        self.doctor_two = Doctor.objects.create(
            created_by=self.user_b,
            name='Doctor Watson',
            email='watson@baker.com',
            phone='5559876543',
            specialization='General Practitioner',
            license_number='DOC-002',
            address='221B Baker St'
        )

    # ------------------ PATIENT API TESTS ------------------

    def test_patients_unauthenticated_fails(self):
        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient_success(self):
        self.client.force_authenticate(user=self.user_a)
        payload = {
            'name': 'New Patient',
            'email': 'newpatient@example.com',
            'phone': '1234567890',
            'date_of_birth': '2000-01-01',
            'gender': 'Other',
            'address': '555 New Road'
        }
        response = self.client.post('/api/patients/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Patient')
        self.assertEqual(response.data['created_by'], self.user_a.id)

    def test_list_patients_scoped_to_authenticated_user(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see patient_a, not patient_b
        names = [p['name'] for p in response.data]
        self.assertIn('Patient Alpha One', names)
        self.assertNotIn('Patient Beta One', names)

    def test_retrieve_patient_detail(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(f'/api/patients/{self.patient_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.patient_a.id)

    def test_update_patient(self):
        self.client.force_authenticate(user=self.user_a)
        payload = {
            'name': 'Patient Alpha Updated',
            'email': 'updated@example.com',
            'phone': '1112223333',
            'date_of_birth': '1985-01-01',
            'gender': 'Female',
            'address': '999 Updated St'
        }
        response = self.client.put(f'/api/patients/{self.patient_a.id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Patient Alpha Updated')

    def test_delete_patient(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.delete(f'/api/patients/{self.patient_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(id=self.patient_a.id).exists())

    # ------------------ DOCTOR API TESTS ------------------

    def test_doctors_unauthenticated_fails(self):
        response = self.client.get('/api/doctors/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_doctor_success(self):
        self.client.force_authenticate(user=self.user_a)
        payload = {
            'name': 'Doctor Meredith Grey',
            'email': 'meredith@seattlegrace.com',
            'phone': '5553334444',
            'specialization': 'General Surgery',
            'license_number': 'DOC-003',
            'address': 'Seattle Grace Hospital'
        }
        response = self.client.post('/api/doctors/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Doctor Meredith Grey')
        self.assertEqual(response.data['created_by'], self.user_a.id)

    def test_list_all_doctors(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get('/api/doctors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # All doctors are listed
        names = [d['name'] for d in response.data]
        self.assertIn('Doctor Strange', names)
        self.assertIn('Doctor Watson', names)

    def test_retrieve_doctor_detail(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(f'/api/doctors/{self.doctor_one.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Doctor Strange')

    def test_update_doctor(self):
        self.client.force_authenticate(user=self.user_a)
        payload = {
            'name': 'Doctor Strange Updated',
            'email': 'strange@marvel.com',
            'phone': '5551234567',
            'specialization': 'Sorcery & Medicine',
            'license_number': 'DOC-001',
            'address': '177A Bleecker St'
        }
        response = self.client.put(f'/api/doctors/{self.doctor_one.id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['specialization'], 'Sorcery & Medicine')

    def test_delete_doctor(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.delete(f'/api/doctors/{self.doctor_one.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doctor.objects.filter(id=self.doctor_one.id).exists())

    # ------------------ PATIENT-DOCTOR MAPPING API TESTS ------------------

    def test_mappings_unauthenticated_fails(self):
        response = self.client.get('/api/mappings/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_mapping_success(self):
        self.client.force_authenticate(user=self.user_a)
        payload = {
            'patient_id': self.patient_a.id,
            'doctor_id': self.doctor_one.id
        }
        response = self.client.post('/api/mappings/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['assigned_by'], self.user_a.id)

    def test_create_duplicate_mapping_fails(self):
        self.client.force_authenticate(user=self.user_a)
        # Create initial mapping
        PatientDoctorMapping.objects.create(
            patient=self.patient_a,
            doctor=self.doctor_one,
            assigned_by=self.user_a
        )
        payload = {
            'patient_id': self.patient_a.id,
            'doctor_id': self.doctor_one.id
        }
        response = self.client.post('/api/mappings/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_all_mappings(self):
        self.client.force_authenticate(user=self.user_a)
        PatientDoctorMapping.objects.create(
            patient=self.patient_a,
            doctor=self.doctor_one,
            assigned_by=self.user_a
        )
        response = self.client.get('/api/mappings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_doctors_assigned_to_specific_patient(self):
        self.client.force_authenticate(user=self.user_a)
        PatientDoctorMapping.objects.create(
            patient=self.patient_a,
            doctor=self.doctor_one,
            assigned_by=self.user_a
        )
        response = self.client.get(f'/api/mappings/{self.patient_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['doctor']['id'], self.doctor_one.id)

    def test_delete_mapping(self):
        self.client.force_authenticate(user=self.user_a)
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient_a,
            doctor=self.doctor_one,
            assigned_by=self.user_a
        )
        response = self.client.delete(f'/api/mappings/{mapping.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PatientDoctorMapping.objects.filter(id=mapping.id).exists())
