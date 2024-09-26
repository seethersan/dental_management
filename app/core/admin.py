from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import (
    Country,
    State,
    City,
    Procedure,
    DoctorClinicAffiliation,
    Clinic,
    Doctor,
    Patient,
)

User = get_user_model()

admin.site.register(User, UserAdmin)


class DoctorClinicAffiliationInline(admin.TabularInline):
    model = DoctorClinicAffiliation
    extra = 1


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ["name", "country"]
    list_filter = ["country"]
    search_fields = ["name"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "state"]
    list_filter = ["state"]
    search_fields = ["name"]


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "phone_number", "country", "state", "city"]
    list_filter = ["country", "state", "city"]
    search_fields = ["name", "address", "phone_number"]


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ["user", "npi"]
    search_fields = ["user__username", "npi"]
    filter_horizontal = ["specialties"]
    inlines = [DoctorClinicAffiliationInline]


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["user", "date_of_birth", "phone_number", "gender"]
    search_fields = ["user__username", "phone_number"]
    list_filter = ["gender"]
