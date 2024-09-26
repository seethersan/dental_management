from django.urls import path
from . import views

urlpatterns = [
    path('patients/', views.add_patient, name='add-patient'),
    path('doctors/', views.add_doctor, name='add-doctor'),
    path('clinics/', views.add_clinic, name='add-clinic'),
    path('clinics/<int:clinic_id>/', views.get_clinic, name='get-clinic'),
]
