import json
from django import forms
from django.contrib.auth import get_user_model
from .models import (
    Patient,
    Doctor,
    Procedure,
    Visit,
    Appointment,
    DoctorClinicAffiliation,
    Clinic,
    Country,
    State,
    City,
)

User = get_user_model()


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["date_of_birth", "address", "phone_number", "ssn_last_four", "gender"]


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ["visit_date", "doctor", "clinic", "procedures_done", "doctor_notes"]

    visit_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )  # For DateTime picker

    # Add custom styling or widget for the procedures field if needed
    procedures_done = forms.ModelMultipleChoiceField(
        queryset=Procedure.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Use checkboxes for multi-select
    )


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["procedure", "clinic", "doctor", "appointment_date"]

    # Initialize fields with an empty queryset to be populated later
    procedure = forms.ModelChoiceField(
        queryset=Procedure.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    clinic = forms.ModelChoiceField(
        queryset=Clinic.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )  # Queryset set to none initially
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )  # Queryset set to none initially
    appointment_date = forms.DateTimeField(
        widget=forms.Select(attrs={"class": "form-select"})
    )  # Dynamic based on available time slots


class DoctorForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        help_text="Enter username for the doctor",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    email = forms.EmailField(
        max_length=255,
        help_text="Enter email for the doctor",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="Enter password for the doctor",
    )

    class Meta:
        model = Doctor
        fields = ["phone_number", "npi", "specialties"]
        widgets = {
            "specialties": forms.CheckboxSelectMultiple(),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["npi"].widget.attrs.update({"class": "form-control"})


class DoctorUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    npi = forms.CharField(
        label="NPI", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    specialties = forms.ModelMultipleChoiceField(
        queryset=Procedure.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Specialties",
    )

    class Meta:
        model = Doctor
        fields = ["phone_number", "npi", "specialties"]  # Include NPI and specialties
        widgets = {
            "specialties": forms.CheckboxSelectMultiple(),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the username read-only by setting the disabled attribute
        self.fields["username"] = forms.CharField(
            label="Username",
            disabled=True,
            initial=kwargs["instance"].user.username if "instance" in kwargs else "",
            widget=forms.TextInput(attrs={"class": "form-control"}),
        )


class DoctorClinicAffiliationForm(forms.ModelForm):
    class Meta:
        model = DoctorClinicAffiliation
        fields = ["doctor", "office_address", "working_schedule"]

    def __init__(self, *args, **kwargs):
        clinic = kwargs.pop("clinic", None)
        super(DoctorClinicAffiliationForm, self).__init__(*args, **kwargs)
        if clinic:
            self.fields["doctor"].queryset = clinic.doctors.all()

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor")
        clinic = (
            self.instance.clinic if self.instance.pk else cleaned_data.get("clinic")
        )

        # Check if the doctor-clinic affiliation already exists
        if doctor and clinic:
            if (
                DoctorClinicAffiliation.objects.filter(doctor=doctor, clinic=clinic)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise forms.ValidationError(
                    "This doctor is already affiliated with this clinic."
                )

        return cleaned_data


class ClinicForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = ["name", "address", "phone_number", "country", "state", "city"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.Select(attrs={"class": "form-select", "id": "id_country"}),
            "state": forms.Select(
                attrs={"class": "form-select", "id": "id_state", "disabled": "true"}
            ),  # Disable by default
            "city": forms.Select(
                attrs={"class": "form-select", "id": "id_city", "disabled": "true"}
            ),  # Disable by default
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initially load only the country data, don't populate state or city
        self.fields["state"].queryset = State.objects.none()
        self.fields["city"].queryset = City.objects.none()


class ClinicUpdateForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = ["name", "address", "phone_number", "country", "state", "city"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.Select(attrs={"class": "form-select", "id": "id_country"}),
            "state": forms.Select(attrs={"class": "form-select", "id": "id_state"}),
            "city": forms.Select(attrs={"class": "form-select", "id": "id_city"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["state"].queryset = State.objects.filter(
            country=self.instance.country
        )
        self.fields["city"].queryset = City.objects.filter(state=self.instance.state)

        self.initial["state"] = self.instance.state
        self.initial["city"] = self.instance.city


class PatientForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"}), required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}), required=True
    )

    class Meta:
        model = Patient
        fields = ["date_of_birth", "address", "phone_number", "ssn_last_four", "gender"]
        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "ssn_last_four": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
        }


class PatientUpdateForm(forms.ModelForm):
    # Add user fields for first name and last name
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Patient
        fields = ["date_of_birth", "address", "phone_number", "ssn_last_four", "gender"]
        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "ssn_last_four": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name


class DoctorClinicAffiliationForm(forms.ModelForm):
    class Meta:
        model = DoctorClinicAffiliation
        fields = ["doctor", "office_address", "working_schedule"]

    def __init__(self, *args, **kwargs):
        self.clinic = kwargs.pop("clinic", None)  # Get clinic from kwargs
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor")

        # Ensure clinic is available (either from the form or the instance)
        clinic = self.clinic or self.instance.clinic

        # Check if this doctor-clinic affiliation already exists
        if (
            DoctorClinicAffiliation.objects.filter(doctor=doctor, clinic=clinic)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError(
                f"Doctor {doctor.user.get_full_name()} is already affiliated with this clinic."
            )

        return cleaned_data

    def clean_working_schedule(self):
        schedule_data = self.cleaned_data["working_schedule"]

        # Ensure that the schedule is valid JSON (it should be a list, not a string)
        if schedule_data:
            try:
                if isinstance(schedule_data, list):
                    # It's already a list, so no need to split or process it as a string
                    return json.dumps(schedule_data)  # Store as JSON string
                else:
                    # If it's a string, attempt to parse it as JSON
                    return json.dumps(json.loads(schedule_data))
            except ValueError:
                raise forms.ValidationError("Invalid working schedule format")

        return schedule_data
