from rest_framework import serializers
from healthcare.models import Patient, Doctor, PatientDoctorMapping

class PatientSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.name')

    class Meta:
        model = Patient
        fields = (
            'id',
            'created_by',
            'created_by_name',
            'name',
            'email',
            'phone',
            'date_of_birth',
            'gender',
            'address',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_by_name', 'created_at', 'updated_at')

class DoctorSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.name')

    class Meta:
        model = Doctor
        fields = (
            'id',
            'created_by',
            'created_by_name',
            'name',
            'email',
            'phone',
            'specialization',
            'license_number',
            'address',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_by_name', 'created_at', 'updated_at')

class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        source='doctor',
        write_only=True
    )
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    assigned_by_name = serializers.ReadOnlyField(source='assigned_by.name')

    class Meta:
        model = PatientDoctorMapping
        fields = (
            'id',
            'patient_id',
            'doctor_id',
            'patient',
            'doctor',
            'assigned_by',
            'assigned_by_name',
            'assigned_at',
        )
        read_only_fields = ('id', 'patient', 'doctor', 'assigned_by', 'assigned_by_name', 'assigned_at')

    def validate(self, attrs):
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError({
                "detail": f"Doctor '{doctor.name}' is already assigned to patient '{patient.name}'."
            })
        return attrs
