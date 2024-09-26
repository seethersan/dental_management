$(document).ready(function () {
    // Load doctors based on the selected clinic
    $('#id_clinic').change(function () {
        var clinicId = $(this).val();
        if (clinicId) {
            $.ajax({
                url: "/ajax/load-doctors/",
                data: {
                    'clinic_id': clinicId
                },
                success: function (data) {
                    $('#id_doctor').empty().append('<option value="">Select a doctor</option>');
                    $('#id_doctor').prop('disabled', false);
                    $.each(data, function (key, value) {
                        $('#id_doctor').append('<option value="' + value.id + '">' + value.name + '</option>');
                    });
                }
            });
        } else {
            $('#id_doctor').empty().prop('disabled', true);
            $('#id_visit_date').empty().prop('disabled', true);
            $('#procedures-container').empty();
        }
    });

    // Load available time slots and procedures based on the selected doctor
    $('#id_doctor').change(function () {
        var doctorId = $(this).val();
        var clinicId = $('#id_clinic').val();

        if (doctorId) {
            // Load available time slots
            $.ajax({
                url: "/ajax/load-timeslots/",
                data: {
                    'doctor_id': doctorId,
                    'clinic_id': clinicId
                },
                success: function (data) {
                    $('#id_visit_date').empty().append('<option value="">Select a time slot</option>');
                    $('#id_visit_date').prop('disabled', false);
                    $.each(data, function (key, value) {
                        $('#id_visit_date').append('<option value="' + value.start + '">' + value.start + ' - ' + value.end + '</option>');
                    });
                }
            });

            // Load procedures for the doctor
            $.ajax({
                url: "/ajax/load-procedures/",
                data: {
                    'doctor_id': doctorId
                },
                success: function (data) {
                    $('#procedures-container').empty();
                    $.each(data, function (key, value) {
                        $('#procedures-container').append(
                            '<div class="form-check">' +
                            '<input type="checkbox" class="form-check-input" name="procedures_done" value="' + value.id + '" id="procedure_' + value.id + '">' +
                            '<label class="form-check-label" for="procedure_' + value.id + '">' + value.name + '</label>' +
                            '</div>'
                        );
                    });
                }
            });
        } else {
            $('#id_visit_date').empty().prop('disabled', true);
            $('#procedures-container').empty();
        }
    });
});
