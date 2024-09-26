from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import (
    Doctor,
    Clinic,
    DoctorClinicAffiliation,
    Patient,
    Visit,
    Procedure,
    Appointment,
)

User = get_user_model()


class AffiliationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="doctoruser", email="doctor@example.com", password="12345"
        )
        self.clinic = Clinic.objects.create(name="Test Clinic", address="123 Clinic St")
        self.doctor = Doctor.objects.create(user=self.user, npi="1234567890")
        self.affiliation_url = reverse("create-affiliation", args=[self.clinic.id])
        self.edit_affiliation_url = reverse("edit-affiliation", args=[1])
        self.delete_affiliation_url = reverse("delete-affiliation", args=[1])

    def test_create_affiliation(self):
        """Test creating a doctor-clinic affiliation"""
        self.client.login(username="doctoruser", password="12345")

        data = {
            "doctor": self.doctor.id,
            "office_address": "123 Clinic St",
            "working_schedule": '[{"start": "2024-09-26T09:00:00", "end": "2024-09-26T10:00:00"}]',
        }
        response = self.client.post(self.affiliation_url, data)

        # Ensure the response is a redirect (success)
        self.assertEqual(response.status_code, 302)

        # Ensure the affiliation was created
        affiliation = DoctorClinicAffiliation.objects.get(
            doctor=self.doctor, clinic=self.clinic
        )
        self.assertEqual(affiliation.office_address, "123 Clinic St")
        self.assertEqual(
            affiliation.working_schedule[0]["start"], "2024-09-26T09:00:00"
        )

    def test_edit_affiliation(self):
        """Test editing an affiliation's working schedule"""
        affiliation = DoctorClinicAffiliation.objects.create(
            doctor=self.doctor,
            clinic=self.clinic,
            office_address="123 Clinic St",
            working_schedule=[
                {"start": "2024-09-26T09:00:00", "end": "2024-09-26T10:00:00"}
            ],
        )
        edit_url = reverse("edit-affiliation", args=[affiliation.id])

        # Edit the affiliation
        data = {
            "doctor": self.doctor.id,
            "office_address": "456 New St",
            "working_schedule": '[{"start": "2024-09-26T11:00:00", "end": "2024-09-26T12:00:00"}]',
        }
        response = self.client.post(edit_url, data)
        self.assertEqual(response.status_code, 302)

        # Ensure affiliation was updated
        affiliation.refresh_from_db()
        self.assertEqual(affiliation.office_address, "456 New St")
        self.assertEqual(
            affiliation.working_schedule[0]["start"], "2024-09-26T11:00:00"
        )

    def test_delete_affiliation(self):
        """Test deleting an affiliation"""
        affiliation = DoctorClinicAffiliation.objects.create(
            doctor=self.doctor,
            clinic=self.clinic,
            office_address="123 Clinic St",
            working_schedule=[
                {"start": "2024-09-26T09:00:00", "end": "2024-09-26T10:00:00"}
            ],
        )
        delete_url = reverse("delete-affiliation", args=[affiliation.id])

        # Delete the affiliation
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)

        # Ensure the affiliation was deleted
        self.assertFalse(
            DoctorClinicAffiliation.objects.filter(id=affiliation.id).exists()
        )


class VisitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="patientuser", email="patient@example.com", password="12345"
        )
        self.patient = Patient.objects.create(
            user=self.user,
            date_of_birth="1990-01-01",
            address="456 Patient St",
            phone_number="555-555-5555",
            ssn_last_four="1234",
            gender="M",
        )
        self.doctor_user = User.objects.create_user(
            username="doctoruser", email="doctor@example.com", password="12345"
        )
        self.doctor = Doctor.objects.create(user=self.doctor_user, npi="1234567890")
        self.clinic = Clinic.objects.create(name="Test Clinic", address="123 Clinic St")

        self.visit_url = reverse("add-visit", args=[self.patient.id])
        self.appointment_url = reverse("schedule-appointment", args=[self.patient.id])

    def test_add_visit(self):
        """Test adding a new visit for a patient"""
        self.client.login(username="patientuser", password="12345")

        # Create a procedure
        procedure = Procedure.objects.create(name="Teeth Cleaning")

        data = {
            "doctor": self.doctor.id,  # Ensure this doctor exists
            "clinic": self.clinic.id,  # Ensure this clinic exists
            "procedures_done": [procedure.id],  # Valid procedure ID list
            "visit_date": "2024-09-26T09:00:00",  # Add a valid visit date
            "doctor_notes": "Routine checkup",
        }
        response = self.client.post(self.visit_url, data)

        # Print form errors if the response is not a redirect
        if response.status_code == 200:
            print(response.context["form"].errors)

        # Ensure the response is a redirect (success)
        self.assertEqual(response.status_code, 302)

        # Ensure the visit was created
        visit = Visit.objects.get(patient=self.patient, doctor=self.doctor)
        self.assertEqual(visit.doctor_notes, "Routine checkup")

    def test_schedule_appointment(self):
        """Test scheduling an appointment for a patient"""
        self.client.login(username="patientuser", password="12345")

        # Create a procedure
        procedure = Procedure.objects.create(name="Teeth Cleaning")

        # Ensure the doctor is affiliated with the clinic before scheduling
        DoctorClinicAffiliation.objects.create(
            doctor=self.doctor,
            clinic=self.clinic,
            office_address="123 Clinic St",
            working_schedule=[
                {"start": "2024-09-26T09:00:00", "end": "2024-09-26T10:00:00"}
            ],
        )

        # Now test scheduling the appointment with a valid doctor and clinic
        data = {
            "clinic": self.clinic.id,  # Valid clinic
            "doctor": self.doctor.id,  # Valid doctor for the clinic
            "procedure": procedure.id,  # Valid procedure ID
            "appointment_date": "2024-09-26T09:00:00",  # Valid appointment date
        }
        response = self.client.post(self.appointment_url, data)

        # Print form errors if the response is not a redirect
        if response.status_code == 200:
            print(response.context["form"].errors)

        # Ensure the response is a redirect (success)
        self.assertEqual(response.status_code, 302)

        # Ensure the appointment was created in the database
        appointment = Appointment.objects.get(patient=self.patient, doctor=self.doctor)
        self.assertEqual(appointment.procedure.id, procedure.id)
        self.assertEqual(appointment.clinic.id, self.clinic.id)
        self.assertEqual(
            appointment.appointment_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "2024-09-26T09:00:00",
        )
