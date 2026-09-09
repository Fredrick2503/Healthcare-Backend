from django.db import models
from django.conf import settings

class Patient(models.Model):
    """
    Patient entity strictly matching ER diagram:
    id PK, created_by FK, name, email, phone, date_of_birth, gender, address, created_at, updated_at
    """
    id = models.BigAutoField(primary_key=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_patients',
        db_column='created_by'
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"

class Doctor(models.Model):
    """
    Doctor entity strictly matching ER diagram:
    id PK, created_by FK, name, email, phone, specialization, license_number, address, created_at, updated_at
    """
    id = models.BigAutoField(primary_key=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_doctors',
        db_column='created_by'
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    specialization = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'doctors'
        ordering = ['-created_at']

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"

class PatientDoctorMapping(models.Model):
    """
    Patient-Doctor Mapping entity strictly matching ER diagram:
    id PK, patient_id FK, doctor_id FK, assigned_by FK, assigned_at
    """
    id = models.BigAutoField(primary_key=True)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='doctor_mappings',
        db_column='patient_id'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='patient_mappings',
        db_column='doctor_id'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_mappings',
        db_column='assigned_by'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'patient_doctor_mappings'
        unique_together = ('patient', 'doctor')
        ordering = ['-assigned_at']

    def __str__(self):
        return f"Mapping: {self.patient.name} -> Dr. {self.doctor.name}"
