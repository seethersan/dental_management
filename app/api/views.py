from rest_framework import generics
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from core.models import Patient, Doctor, Clinic
from .serializers import PatientSerializer, DoctorSerializer, ClinicSerializer


# Add a new patient (CBV)
class AddPatientView(generics.CreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]  # Permissions


# Add a new doctor (CBV)
class AddDoctorView(generics.CreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


# Add a new clinic (CBV)
class AddClinicView(generics.CreateAPIView):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


# Get clinic information (CBV)
class GetClinicView(generics.RetrieveAPIView):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    lookup_field = "id"
