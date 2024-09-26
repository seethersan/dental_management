var calendar;

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        selectable: true,  // Allow selecting time slots
        editable: true,    // Allow modifying time slots
        slotDuration: '01:00:00',  // Set each slot to 1 hour
        allDaySlot: false, // Hide the all-day slot
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'timeGridWeek,timeGridDay'
        },
        select: function(info) {
            // Capture the selected start and end times
            var startTime = info.startStr;
            var endTime = info.endStr;
            
            addEventToForm(startTime, endTime);
        },
        events: loadExistingEvents()  // Load existing events if any
    });
    calendar.render();
});

// Function to load existing events from the hidden field into FullCalendar
function loadExistingEvents() {
    var events = [];
    var scheduleField = document.getElementById('id_working_schedule').value;

    if (scheduleField && scheduleField.trim()) {
        try {
            var schedule = JSON.parse(scheduleField);  // Parse stored JSON
            if (Array.isArray(schedule)) {
                schedule.forEach(function(event) {
                    events.push({
                        start: event.start,
                        end: event.end,
                        allDay: false
                    });
                });
            }
        } catch (e) {
            console.error("Invalid JSON in working schedule:", e);
        }
    }
    return events;
}

// Function to add selected time slots to the hidden form field
function addEventToForm(startTime, endTime) {
    var scheduleField = document.getElementById('id_working_schedule');
    var currentSchedule = [];

    // Check if scheduleField has valid JSON, if not, initialize an empty array
    if (scheduleField.value && scheduleField.value.trim()) {
        try {
            currentSchedule = JSON.parse(scheduleField.value) || [];
        } catch (e) {
            console.error("Invalid JSON in working schedule:", e);
            currentSchedule = [];
        }
    }

    var newEvent = {
        start: startTime,
        end: endTime
    };

    // Add new event to the current schedule
    currentSchedule.push(newEvent);

    // Update the hidden input with the new schedule
    scheduleField.value = JSON.stringify(currentSchedule);

    // Add the new event to FullCalendar dynamically
    calendar.addEvent(newEvent);
}