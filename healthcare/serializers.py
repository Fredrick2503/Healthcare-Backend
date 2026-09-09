from rest_framework import serializers
from healthcare.models import Patient, Doctor, PatientDoctorMapping

class PatientSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(
        source='created_by.name',
        help_text="Name of the user who registered this patient"
    )

    name = serializers.CharField(
        help_text="Patient's full legal name (e.g. John Doe)"
    )
    email = serializers.EmailField(
        help_text="Patient's contact email address"
    )
    phone = serializers.CharField(
        help_text="Contact telephone number (e.g. +1-555-123-4567)"
    )
    date_of_birth = serializers.DateField(
        help_text="Patient date of birth in YYYY-MM-DD format (e.g. 1990-05-15)"
    )
    gender = serializers.CharField(
        help_text="Gender identity (e.g. Male, Female, Other)"
    )
    address = serializers.CharField(
        help_text="Full residential street address"
    )

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
    created_by_name = serializers.ReadOnlyField(
        source='created_by.name',
        help_text="Name of the user who registered this doctor"
    )

    name = serializers.CharField(
        help_text="Doctor's full name (e.g. Gregory House)"
    )
    email = serializers.EmailField(
        help_text="Professional contact email"
    )
    phone = serializers.CharField(
        help_text="Clinic or office contact number"
    )
    specialization = serializers.CharField(
        help_text="Medical specialty (e.g. Diagnostic Medicine, General Surgery)"
    )
    license_number = serializers.CharField(
        help_text="State or national medical license registration number"
    )
    address = serializers.CharField(
        help_text="Hospital, clinic, or practice facility address"
    )

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
        write_only=True,
        help_text="Primary Key ID of the Patient to assign"
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        source='doctor',
        write_only=True,
        help_text="Primary Key ID of the Doctor to assign"
    )
    patient = PatientSerializer(read_only=True, help_text="Assigned patient details")
    doctor = DoctorSerializer(read_only=True, help_text="Assigned doctor details")
    assigned_by_name = serializers.ReadOnlyField(
        source='assigned_by.name',
        help_text="Name of the staff member who made the assignment"
    )

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
