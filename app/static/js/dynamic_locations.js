document.addEventListener('DOMContentLoaded', function () {
    const countryElement = document.getElementById('id_country');
    const stateElement = document.getElementById('id_state');
    const cityElement = document.getElementById('id_city');

    // Enable state and city dropdowns if they have preloaded values
    if (stateElement.value) {
        stateElement.disabled = false;
    }
    if (cityElement.value) {
        cityElement.disabled = false;
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

                // Populate the state dropdown and preselect if applicable
                data.forEach(state => {
                    const option = document.createElement('option');
                    option.value = state.id;
                    option.textContent = state.name;
                    stateElement.appendChild(option);

                    // Preserve the selected state
                    if (selectedStateId && state.id == selectedStateId) {
                        option.selected = true;
                        stateElement.disabled = false;
                    }
                });

                // After loading states, trigger loading cities if a state is preselected
                if (selectedStateId && selectedCityId == null) {
                    loadCities(selectedStateId, cityElement.value);  // Pass selected city ID
                }
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

                // Populate the city dropdown and preselect if applicable
                data.forEach(city => {
                    const option = document.createElement('option');
                    option.value = city.id;
                    option.textContent = city.name;
                    cityElement.appendChild(option);

                    // Preserve the selected city
                    if (selectedCityId && city.id == selectedCityId) {
                        option.selected = true;
                        cityElement.disabled = false;
                    }
                });
            })
            .catch(error => console.error('Error fetching cities:', error));
    }

    // Handle country change event
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

    // Handle state change event
    stateElement.addEventListener('change', function () {
        const stateId = this.value;
        if (stateId) {
            loadCities(stateId);  // Load cities based on selected state
        } else {
            cityElement.innerHTML = '<option value="">Select a state first</option>';
            cityElement.disabled = true;
        }
    });

    // Automatically load states and cities if they are preselected
    const selectedCountryId = countryElement.value;
    const selectedStateId = stateElement.value;
    const selectedCityId = cityElement.value;
    if (selectedCountryId) {
        loadStates(selectedCountryId, selectedStateId);  // Preload states and select current state
        if (selectedStateId) {
            loadCities(selectedStateId, selectedCityId);  // Preload cities and select current city
        }
    }
});
