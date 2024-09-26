$(document).ready(function () {
    // Load clinics based on the selected procedure
    $('#id_procedure').change(function () {
        var procedureId = $(this).val();
        if (procedureId) {
            $.ajax({
                url: "/ajax/load-clinics/",
                data: {
                    'procedure_id': procedureId
                },
                success: function (data) {
                    $('#id_clinic').empty().append('<option value="">Select a clinic</option>');
                    $.each(data, function (key, value) {
                        $('#id_clinic').append('<option value="' + value.id + '">' + value.name + '</option>');
                    });
                    $('#id_clinic').prop('disabled', false);
                }
            });
        } else {
            $('#id_clinic').empty().prop('disabled', true);
            $('#id_doctor').empty().prop('disabled', true);
            $('#id_appointment_date').empty().prop('disabled', true);
        }
    });

    // Load doctors based on the selected clinic and procedure
    $('#id_clinic').change(function () {
        var procedureId = $('#id_procedure').val();
        var clinicId = $(this).val();
        if (clinicId) {
            $.ajax({
                url: "/ajax/load-doctors/",
                data: {
                    'procedure_id': procedureId,
                    'clinic_id': clinicId
                },
                success: function (data) {
                    $('#id_doctor').empty().append('<option value="">Select a doctor</option>');
                    $.each(data, function (key, value) {
                        $('#id_doctor').append('<option value="' + value.id + '">' + value.name + '</option>');
                    });
                    $('#id_doctor').prop('disabled', false);
                }
            });
        } else {
            $('#id_doctor').empty().prop('disabled', true);
            $('#id_appointment_date').empty().prop('disabled', true);
        }
    });

    // Load available time slots based on the selected doctor and clinic
    $('#id_doctor').change(function () {
        var doctorId = $(this).val();
        var clinicId = $('#id_clinic').val();
        if (doctorId) {
            $.ajax({
                url: "/ajax/load-timeslots/",
                data: {
                    'doctor_id': doctorId,
                    'clinic_id': clinicId
                },
                success: function (data) {
                    $('#id_appointment_date').empty().append('<option value="">Select a time slot</option>');
                    $.each(data, function (key, value) {
                        $('#id_appointment_date').append('<option value="' + value.start + '">' + value.start + ' - ' + value.end + '</option>');
                    });
                    $('#id_appointment_date').prop('disabled', false);
                }
            });
        } else {
            $('#id_appointment_date').empty().prop('disabled', true);
        }
    });
});
