import json
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    TemplateView,
)
from django.contrib.auth import get_user_model
from .models import (
    Doctor,
    Clinic,
    Procedure,
    DoctorClinicAffiliation,
    Patient,
    Visit,
    Appointment,
    State,
    City,
)
from django.db.models import Count, Q, F
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    ClinicForm,
    ClinicUpdateForm,
    DoctorForm,
    DoctorUpdateForm,
    PatientForm,
    PatientUpdateForm,
    VisitForm,
    AppointmentForm,
    DoctorClinicAffiliationForm,
)

User = get_user_model()


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "core/home.html"
    login_url = "login"


def load_states(request):
    country_id = request.GET.get("country_id")
    states = State.objects.filter(country_id=country_id).order_by("name")
    return JsonResponse(list(states.values("id", "name")), safe=False)


def load_cities(request):
    state_id = request.GET.get("state_id")
    cities = City.objects.filter(state_id=state_id).order_by("name")
    return JsonResponse(list(cities.values("id", "name")), safe=False)


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "core/profile.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class EditUserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ["first_name", "last_name", "email"]
    template_name = "core/edit_profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self):
        return self.request.user


class PatientListView(ListView):
    model = Patient
    template_name = "core/patient_list.html"
    context_object_name = "patients"

    def get_queryset(self):
        queryset = super().get_queryset()
        for patient in queryset:
            patient.last_visit = (
                Visit.objects.filter(patient=patient).order_by("-visit_date").first()
            )
            patient.next_appointment = (
                Appointment.objects.filter(patient=patient)
                .order_by("appointment_date")
                .first()
            )
        return queryset


class PatientCreateView(LoginRequiredMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = "core/patient_form.html"
    success_url = reverse_lazy(
        "patient-list"
    )  # Redirect after successful patient creation

    def form_valid(self, form):
        # Extract the user data from the form
        username = form.cleaned_data["username"]
        first_name = form.cleaned_data["first_name"]
        last_name = form.cleaned_data["last_name"]
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        # Create the User object
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Associate the new User with the Patient instance
        patient = form.save(commit=False)  # Don't commit to the database yet
        patient.user = user  # Link the newly created User
        patient.save()  # Now save the Patient instance with the linked User

        return super().form_valid(form)


class PatientDetailView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = "core/patient_detail.html"
    context_object_name = "patient"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["visits"] = Visit.objects.filter(patient=self.object).order_by(
            "-visit_date"
        )
        context["next_appointment"] = (
            Appointment.objects.filter(patient=self.object)
            .order_by("appointment_date")
            .first()
        )
        return context


class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientUpdateForm
    template_name = "core/patient_update.html"
    context_object_name = "patient"
    success_url = reverse_lazy(
        "patient-list"
    )  # Redirect to patient list after successful update

    def form_valid(self, form):
        # Save the user's first name and last name
        patient = form.save(commit=False)
        patient.user.first_name = form.cleaned_data["first_name"]
        patient.user.last_name = form.cleaned_data["last_name"]
        patient.user.save()  # Save changes to the User model
        patient.save()  # Save changes to the Patient model
        return super().form_valid(form)


class ClinicListView(LoginRequiredMixin, ListView):
    model = Clinic
    template_name = "core/clinic_list.html"
    context_object_name = "clinics"

    def get_queryset(self):
        return Clinic.objects.annotate(
            num_doctors=Count("doctorclinicaffiliation__doctor", distinct=True),
            num_patients=Count(
                # Count distinct patients with either a visit or appointment to this clinic
                "visit__patient", 
                filter=Q(visit__clinic=F("pk")) | Q(appointment__clinic=F("pk")),
                distinct=True,
            )
        )


class ClinicDetailView(LoginRequiredMixin, DetailView):
    model = Clinic
    template_name = "core/clinic_detail.html"
    context_object_name = "clinic"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all doctor affiliations for this clinic
        clinic = self.get_object()
        affiliations = DoctorClinicAffiliation.objects.filter(clinic=clinic)

        # Parse the working schedules for each affiliation
        affiliation_data = []
        for affiliation in affiliations:
            try:
                working_schedule = affiliation.working_schedule  # Parse JSON schedule
            except ValueError:
                working_schedule = []  # If there's an error parsing, use an empty list

            # Add affiliation id to the data
            affiliation_data.append(
                {
                    "id": affiliation.id,  # Add the ID for reverse URL matching
                    "doctor": affiliation.doctor.user.get_full_name(),
                    "office_address": affiliation.office_address,
                    "working_schedule": working_schedule,  # Pass the schedule as a list of dicts
                }
            )

        # Add the parsed affiliation data to the context
        context["affiliations"] = affiliation_data
        return context


class ClinicUpdateView(LoginRequiredMixin, UpdateView):
    model = Clinic
    form_class = ClinicUpdateForm
    template_name = "core/clinic_update.html"
    success_url = reverse_lazy("clinic-list")


class DoctorListView(ListView):
    model = Doctor
    template_name = "core/doctor_list.html"
    context_object_name = "doctors"

    def get_queryset(self):
        return Doctor.objects.annotate(
            num_clinics=Count("clinics", distinct=True),
            num_patients=Count("doctorpatientaffiliation__patient", distinct=True),
        )


class ClinicCreateView(LoginRequiredMixin, CreateView):
    model = Clinic
    form_class = ClinicForm
    template_name = "core/clinic_form.html"
    success_url = reverse_lazy("clinic-list")


class DoctorCreateView(CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = "core/doctor_form.html"
    success_url = reverse_lazy("doctor-list")

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        first_name = form.cleaned_data["first_name"]
        last_name = form.cleaned_data["last_name"]
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        # Create the User object
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Assign the user to the doctor instance
        form.instance.user = user

        # You can also handle clinics here if necessary (like linking them programmatically)
        return super().form_valid(form)


class DoctorDetailView(LoginRequiredMixin, DetailView):
    model = Doctor
    template_name = "core/doctor_detail.html"
    context_object_name = "doctor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["affiliations"] = self.object.clinics.all()
        context["patients"] = self.object.patients.all()
        return context


class DoctorUpdateView(LoginRequiredMixin, UpdateView):
    model = Doctor
    form_class = DoctorUpdateForm
    template_name = "core/doctor_update.html"
    context_object_name = "doctor"
    success_url = reverse_lazy("doctor-list")  # Redirect after successful edit

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Set the initial email to the user's email
        form.fields["email"].initial = self.object.user.email
        return form

    def form_valid(self, form):
        # Save the updated doctor data (NPI, specialties)
        doctor = form.save(commit=False)

        # Save the updated user data (email)
        doctor.user.email = form.cleaned_data["email"]
        doctor.user.first_name = form.cleaned_data["first_name"]
        doctor.user.last_name = form.cleaned_data["last_name"]
        doctor.user.save()

        # Save the doctor, including updating the ManyToManyField (specialties)
        doctor.save()
        form.save_m2m()

        return super().form_valid(form)


def create_affiliation(request, clinic_id):
    clinic = get_object_or_404(Clinic, pk=clinic_id)
    if request.method == "POST":
        form = DoctorClinicAffiliationForm(request.POST, clinic=clinic)
        if form.is_valid():
            affiliation = form.save(commit=False)
            affiliation.clinic = clinic
            # Process the working schedule from JSON format
            working_schedule = request.POST.get("working_schedule", "[]")
            try:
                # Ensure it's valid JSON before saving
                affiliation.working_schedule = json.loads(working_schedule)
            except ValueError:
                affiliation.working_schedule = []  # If invalid, save as an empty list
            affiliation.save()
            return redirect("clinic-detail", pk=clinic_id)
        else:
            return render(
                request,
                "core/create_affiliation.html",
                {"form": form, "clinic": clinic},
            )
    else:
        form = DoctorClinicAffiliationForm(clinic=clinic)

    return render(
        request, "core/create_affiliation.html", {"form": form, "clinic": clinic}
    )


def edit_affiliation(request, affiliation_id):
    # Retrieve the existing affiliation object
    affiliation = get_object_or_404(DoctorClinicAffiliation, pk=affiliation_id)

    if request.method == "POST":
        # Process the form data
        form = DoctorClinicAffiliationForm(request.POST, instance=affiliation)
        if form.is_valid():
            # Save the form but don't commit yet
            affiliation = form.save(commit=False)

            # Process the working schedule from JSON format
            working_schedule = request.POST.get("working_schedule", "[]")
            try:
                # Ensure it's valid JSON before saving
                affiliation.working_schedule = json.loads(working_schedule)
            except ValueError:
                affiliation.working_schedule = []  # If invalid, save as an empty list

            # Save the affiliation with the new schedule
            affiliation.save()
            return redirect(
                "clinic-detail", pk=affiliation.clinic.id
            )  # Redirect to clinic detail
    else:
        # Parse the existing working schedule into JSON format
        try:
            working_schedule = json.dumps(affiliation.working_schedule)
        except ValueError:
            working_schedule = []  # If invalid, load an empty list

        form = DoctorClinicAffiliationForm(instance=affiliation)

    # Render the form with the existing working schedule
    return render(
        request,
        "core/edit_affiliation.html",
        {
            "form": form,
            "affiliation": affiliation,
            "working_schedule": working_schedule,  # Pass as JSON to the template
        },
    )


def delete_affiliation(request, affiliation_id):
    # Get the affiliation object or return 404 if not found
    affiliation = get_object_or_404(DoctorClinicAffiliation, pk=affiliation_id)

    # Store clinic ID to redirect to clinic detail after deletion
    clinic_id = affiliation.clinic.id

    # Delete the affiliation
    affiliation.delete()

    # Redirect back to the clinic detail page after deletion
    return redirect("clinic-detail", pk=clinic_id)


def add_visit(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    if request.method == "POST":
        form = VisitForm(request.POST)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.patient = patient  # Set the patient for the visit
            visit.save()
            form.save_m2m()  # Save the ManyToManyField (procedures)
            return redirect("patient-detail", pk=patient_id)
    else:
        form = VisitForm()

    return render(request, "core/add_visit.html", {"form": form, "patient": patient})


def schedule_appointment(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    if request.method == "POST":
        form = AppointmentForm(request.POST)

        # Re-populate clinic queryset to ensure validation
        form.fields["clinic"].queryset = Clinic.objects.all()

        # If clinic is selected, populate the doctors queryset accordingly
        clinic_id = request.POST.get("clinic")
        if clinic_id:
            form.fields["doctor"].queryset = Doctor.objects.filter(
                clinics__id=clinic_id
            )

        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient  # Link the appointment to the patient
            appointment.save()
            return redirect("patient-detail", pk=patient_id)
    else:
        form = AppointmentForm()
        # Populate clinics and procedures in GET request
        form.fields["clinic"].queryset = Clinic.objects.all()
        form.fields["doctor"].queryset = Doctor.objects.none()  # Empty initially
        form.fields["procedure"].queryset = Procedure.objects.all()

    return render(
        request, "core/schedule_appointment.html", {"form": form, "patient": patient}
    )


def ajax_load_clinics(request):
    procedure_id = request.GET.get("procedure_id")
    clinics = Clinic.objects.filter(
        doctorclinicaffiliation__doctor__specialties__id=procedure_id
    ).distinct()
    clinic_data = [{"id": clinic.id, "name": clinic.name} for clinic in clinics]
    return JsonResponse(clinic_data, safe=False)


# View to filter doctors based on the selected clinic
def ajax_load_doctors(request):
    procedure_id = request.GET.get("procedure_id")
    clinic_id = request.GET.get("clinic_id")
    doctors = Doctor.objects.filter(
        clinics__id=clinic_id, specialties__id=procedure_id
    ).distinct()
    doctor_data = [
        {"id": doctor.id, "name": doctor.user.get_full_name()} for doctor in doctors
    ]
    return JsonResponse(doctor_data, safe=False)


# View to filter procedures based on the selected doctor
def ajax_load_procedures(request):
    doctor_id = request.GET.get("doctor_id")
    doctor = Doctor.objects.get(id=doctor_id)
    procedures = doctor.specialties.all()
    procedure_data = [
        {"id": procedure.id, "name": procedure.name} for procedure in procedures
    ]
    return JsonResponse(procedure_data, safe=False)


# View to filter available time slots based on doctor and clinic
def ajax_load_timeslots(request):
    doctor_id = request.GET.get("doctor_id")
    clinic_id = request.GET.get("clinic_id")

    # Get the doctor's working schedule in the selected clinic
    affiliation = DoctorClinicAffiliation.objects.get(
        doctor_id=doctor_id, clinic_id=clinic_id
    )
    working_schedule = affiliation.working_schedule  # Assuming it's a JSON object

    # Fetch booked appointments to exclude them
    booked_appointments = Appointment.objects.filter(
        doctor_id=doctor_id, clinic_id=clinic_id
    ).values_list("appointment_date", flat=True)

    # Calculate available slots, excluding booked ones
    available_slots = []
    for entry in working_schedule:
        start = datetime.fromisoformat(entry["start"])
        end = datetime.fromisoformat(entry["end"])

        # Check if this slot is booked
        if start not in booked_appointments:
            available_slots.append({"start": start.isoformat(), "end": end.isoformat()})

    return JsonResponse(available_slots, safe=False)
