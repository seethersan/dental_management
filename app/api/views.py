from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from core.models import Patient, Doctor, Clinic
from .serializers import PatientSerializer, DoctorSerializer, ClinicSerializer

# Add a new patient
@api_view(['POST'])
def add_patient(request):
    if request.method == 'POST':
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Add a new doctor
@api_view(['POST'])
def add_doctor(request):
    if request.method == 'POST':
        serializer = DoctorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Add a new clinic
@api_view(['POST'])
def add_clinic(request):
    if request.method == 'POST':
        serializer = ClinicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get clinic information (without affiliated patients and doctors)
@api_view(['GET'])
def get_clinic(request, clinic_id):
    try:
        clinic = Clinic.objects.get(id=clinic_id)
    except Clinic.DoesNotExist:
        return Response({'error': 'Clinic not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ClinicSerializer(clinic)
    return Response(serializer.data)
