from rest_framework import serializers
from core.models import Patient, Doctor, Clinic


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "user",
            "date_of_birth",
            "address",
            "phone_number",
            "ssn_last_four",
            "gender",
        ]


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["user", "npi", "specialties"]


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = ["name", "address", "phone_number", "country", "state", "city"]
