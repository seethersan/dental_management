document.addEventListener('DOMContentLoaded', function () {
    const countryElement = document.getElementById('id_country');
    const stateElement = document.getElementById('id_state');
    const cityElement = document.getElementById('id_city');

    // Initially disable state and city dropdowns
    if (!stateElement.value) {
        stateElement.disabled = true;
    }
    if (!cityElement.value) {
        cityElement.disabled = true;
    }

    // Function to load states dynamically based on the selected country
    function loadStates(countryId, selectedStateId = null) {
        const url = '/ajax/load-states/';
        fetch(url + '?country_id=' + countryId)
            .then(response => response.json())
            .then(data => {
                stateElement.innerHTML = '<option value="">Select a state</option>';
                cityElement.innerHTML = '<option value="">Select a state first</option>';
                stateElement.disabled = false;
                cityElement.disabled = true;

                // Populate the state dropdown
                data.forEach(state => {
                    const option = document.createElement('option');
                    option.value = state.id;
                    option.textContent = state.name;
                    stateElement.appendChild(option);

                    // Preselect the state if provided
                    if (selectedStateId && state.id == selectedStateId) {
                        option.selected = true;
                    }
                });
            })
            .catch(error => console.error('Error fetching states:', error));
    }

    // Function to load cities dynamically based on the selected state
    function loadCities(stateId, selectedCityId = null) {
        const url = '/ajax/load-cities/';
        fetch(url + '?state_id=' + stateId)
            .then(response => response.json())
            .then(data => {
                cityElement.innerHTML = '<option value="">Select a city</option>';
                cityElement.disabled = false;

                // Populate the city dropdown
                data.forEach(city => {
                    const option = document.createElement('option');
                    option.value = city.id;
                    option.textContent = city.name;
                    cityElement.appendChild(option);

                    // Preselect the city if provided
                    if (selectedCityId && city.id == selectedCityId) {
                        option.selected = true;
                    }
                });
            })
            .catch(error => console.error('Error fetching cities:', error));
    }

    // Handle country change event
    if (countryElement) {
        countryElement.addEventListener('change', function () {
            const countryId = this.value;
            if (countryId) {
                loadStates(countryId);  // Load states based on selected country
            } else {
                stateElement.innerHTML = '<option value="">Select a country first</option>';
                cityElement.innerHTML = '<option value="">Select a state first</option>';
                stateElement.disabled = true;
                cityElement.disabled = true;
            }
        });
    }

    // Handle state change event
    if (stateElement) {
        stateElement.addEventListener('change', function () {
            const stateId = this.value;
            if (stateId) {
                loadCities(stateId);  // Load cities based on selected state
            } else {
                cityElement.innerHTML = '<option value="">Select a state first</option>';
                cityElement.disabled = true;
            }
        });
    }

    // Automatically load states and cities if preselected
    const selectedCountryId = countryElement ? countryElement.value : null;
    const selectedStateId = stateElement ? stateElement.value : null;
    const selectedCityId = cityElement ? cityElement.value : null;
    if (selectedCountryId) {
        loadStates(selectedCountryId, selectedStateId);  // Preload states and select current state
        if (selectedStateId) {
            loadCities(selectedStateId, selectedCityId);  // Preload cities and select current city
        }
    }
});
