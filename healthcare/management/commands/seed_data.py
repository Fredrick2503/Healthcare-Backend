import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from healthcare.models import Patient, Doctor, PatientDoctorMapping

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds the database with realistic dummy users, doctors, patients, and mappings."

    def handle(self, *args, **options):
        self.stdout.write("==> Seeding database with dummy data...")

        # 1. Create Users
        admin_user, _ = User.objects.get_or_create(
            email="admin@whatbytes.com",
            defaults={"name": "System Administrator", "is_staff": True, "is_superuser": True}
        )
        admin_user.set_password("AdminPass123!")
        admin_user.save()

        user1, _ = User.objects.get_or_create(
            email="dr.meredith@seattlegrace.com",
            defaults={"name": "Dr. Meredith Grey"}
        )
        user1.set_password("Password123!")
        user1.save()

        user2, _ = User.objects.get_or_create(
            email="dr.house@ppth.org",
            defaults={"name": "Dr. Gregory House"}
        )
        user2.set_password("Password123!")
        user2.save()

        self.stdout.write(self.style.SUCCESS("[OK] Created 3 users"))

        # 2. Create Doctors
        doctors_data = [
            {
                "created_by": user1,
                "name": "Gregory House",
                "email": "house@ppth.org",
                "phone": "+1-555-010-001",
                "specialization": "Diagnostic Medicine",
                "license_number": "LIC-99882",
                "address": "Princeton-Plainsboro Hospital, NJ"
            },
            {
                "created_by": user1,
                "name": "Meredith Grey",
                "email": "meredith@seattlegrace.com",
                "phone": "+1-555-010-002",
                "specialization": "General Surgery",
                "license_number": "LIC-55441",
                "address": "Grey Sloan Memorial Hospital, Seattle, WA"
            },
            {
                "created_by": user2,
                "name": "Stephen Strange",
                "email": "strange@metrogeneral.org",
                "phone": "+1-555-010-003",
                "specialization": "Neuro Surgery",
                "license_number": "LIC-11223",
                "address": "177A Bleecker Street, New York, NY"
            },
            {
                "created_by": user2,
                "name": "John Watson",
                "email": "watson@bakerstclinic.co.uk",
                "phone": "+44-20-7946-0950",
                "specialization": "General Practice & Trauma",
                "license_number": "LIC-33445",
                "address": "221B Baker Street, London, UK"
            }
        ]

        doctors = []
        for d in doctors_data:
            doc, _ = Doctor.objects.get_or_create(
                license_number=d["license_number"],
                defaults=d
            )
            doctors.append(doc)
        self.stdout.write(self.style.SUCCESS(f"[OK] Created {len(doctors)} doctors"))

        # 3. Create Patients for user1 (Meredith) and user2 (House)
        patients_data = [
            {
                "created_by": user1,
                "name": "Alice Johnson",
                "email": "alice.johnson@example.com",
                "phone": "+1-555-200-001",
                "date_of_birth": datetime.date(1992, 4, 18),
                "gender": "Female",
                "address": "742 Evergreen Terrace, Springfield, OR"
            },
            {
                "created_by": user1,
                "name": "Robert Downey",
                "email": "robert.downey@example.com",
                "phone": "+1-555-200-002",
                "date_of_birth": datetime.date(1975, 9, 3),
                "gender": "Male",
                "address": "10880 Malibu Point, Malibu, CA"
            },
            {
                "created_by": user2,
                "name": "Emma Watson",
                "email": "emma.watson@example.com",
                "phone": "+44-20-7946-0123",
                "date_of_birth": datetime.date(1996, 7, 24),
                "gender": "Female",
                "address": "4 Privet Drive, Little Whinging, Surrey"
            },
            {
                "created_by": user2,
                "name": "Bruce Wayne",
                "email": "bruce.wayne@waynecorp.com",
                "phone": "+1-555-200-004",
                "date_of_birth": datetime.date(1984, 2, 19),
                "gender": "Male",
                "address": "1007 Mountain Drive, Gotham City, NJ"
            }
        ]

        patients = []
        for p in patients_data:
            pat, _ = Patient.objects.get_or_create(
                email=p["email"],
                defaults=p
            )
            patients.append(pat)
        self.stdout.write(self.style.SUCCESS(f"[OK] Created {len(patients)} patients"))

        # 4. Create Patient-Doctor Mappings
        mappings_data = [
            {"patient": patients[0], "doctor": doctors[0], "assigned_by": user1},  # Alice -> House
            {"patient": patients[1], "doctor": doctors[2], "assigned_by": user1},  # Robert -> Strange
            {"patient": patients[2], "doctor": doctors[3], "assigned_by": user2},  # Emma -> Watson
            {"patient": patients[3], "doctor": doctors[1], "assigned_by": user2},  # Bruce -> Meredith
        ]

        created_count = 0
        for m in mappings_data:
            mapping, created = PatientDoctorMapping.objects.get_or_create(
                patient=m["patient"],
                doctor=m["doctor"],
                defaults={"assigned_by": m["assigned_by"]}
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"[OK] Created {created_count} patient-doctor mappings"))

        self.stdout.write(self.style.SUCCESS("\n==> Database seeding complete!"))
