from django.urls import path
from .views import AddPatientView, AddDoctorView, AddClinicView, GetClinicView

urlpatterns = [
    path("patients/", AddPatientView.as_view(), name="add-patient"),
    path("doctors/", AddDoctorView.as_view(), name="add-doctor"),
    path("clinics/", AddClinicView.as_view(), name="add-clinic"),
    path("clinics/<int:id>/", GetClinicView.as_view(), name="get-clinic"),
]
