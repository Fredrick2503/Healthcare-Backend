from django.contrib import admin
from healthcare.models import Patient, Doctor, PatientDoctorMapping

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'gender', 'created_by', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('gender', 'created_at')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'specialization', 'license_number', 'created_by', 'created_at')
    search_fields = ('name', 'email', 'specialization', 'license_number')
    list_filter = ('specialization', 'created_at')

@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'assigned_by', 'assigned_at')
    search_fields = ('patient__name', 'doctor__name')
    list_filter = ('assigned_at',)
