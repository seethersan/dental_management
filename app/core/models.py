from django.conf import settings
from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"


class State(models.Model):
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="states"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Cities"


class Procedure(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Clinic(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    ssn_last_four = models.CharField(max_length=4)
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])

    def __str__(self):
        return self.user.get_full_name()


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    npi = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    specialties = models.ManyToManyField(Procedure)
    clinics = models.ManyToManyField(Clinic, through="DoctorClinicAffiliation")
    patients = models.ManyToManyField(Patient, through="DoctorPatientAffiliation")

    def __str__(self):
        return self.user.get_full_name()


class Visit(models.Model):
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE)
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)
    clinic = models.ForeignKey("Clinic", on_delete=models.CASCADE)
    visit_date = models.DateTimeField()
    procedures_done = models.ManyToManyField(Procedure)
    doctor_notes = models.TextField()

    def __str__(self):
        return f"Visit by {self.patient.user.get_full_name()} on {self.visit_date}"


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    booked_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment on {self.appointment_date} with {self.doctor.user.get_full_name()}"


class DoctorClinicAffiliation(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    office_address = models.CharField(max_length=255)
    working_schedule = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "clinic"], name="unique_affiliation"
            )
        ]

    def __str__(self):
        return f"{self.doctor.name} - {self.clinic.name}"


class DoctorPatientAffiliation(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    visit_date = models.DateField()

    def __str__(self):
        return (
            f"{self.doctor.user.get_full_name()} - {self.patient.user.get_full_name()}"
        )
