// Use relative paths for production
const API_BASE = window.location.origin;

// Global variables to store options
let carOptions = {};
let modelMakeMapping = {};

// Fetch available options when page loads
document.addEventListener('DOMContentLoaded', async function() {
    console.log("Page loaded, fetching options...");

    try {
        const response = await fetch(`${API_BASE}/api/options`);
        console.log("Options response status:", response.status);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        carOptions = data;
        modelMakeMapping = data.model_make_mapping || {};

        console.log("Loaded options:", carOptions);

        populateDropdown('Make', carOptions.makes);
        populateDropdown('Condition', carOptions.conditions);
        populateDropdown('Model', carOptions.models);

        console.log("Dropdowns populated successfully");

        // Add event listener for Make dropdown change
        document.getElementById('Make').addEventListener('change', function() {
            updateModelDropdown(this.value);
        });

    } catch (error) {
        console.error('Failed to load options:', error);
        document.getElementById('result').textContent = 'Failed to load car options. Please refresh the page.';
    }
});

function populateDropdown(elementId, options) {
    const dropdown = document.getElementById(elementId);
    if (!dropdown) return;

    const currentValue = dropdown.value;
    dropdown.innerHTML = '<option value="">Select ' + elementId + '</option>';

    options.forEach(option => {
        const optionElement = document.createElement('option');
        const displayName = option.split('_').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ').replace('Mazda', 'Mazda ').replace('Series', ' Series');

        optionElement.value = option;
        optionElement.textContent = displayName;
        dropdown.appendChild(optionElement);
    });

    if (currentValue && options.includes(currentValue)) {
        dropdown.value = currentValue;
    }
}

function updateModelDropdown(selectedMake) {
    const modelDropdown = document.getElementById('Model');
    const currentModel = modelDropdown.value;

    if (!selectedMake) {
        populateDropdown('Model', carOptions.models);
        return;
    }

    const filteredModels = carOptions.models.filter(model => {
        const makesForThisModel = modelMakeMapping[model] || [];
        return makesForThisModel.includes(selectedMake);
    });

    if (filteredModels.length === 0) {
        populateDropdown('Model', []);
        modelDropdown.innerHTML = '<option value="">No models found for this make</option>';
    } else {
        populateDropdown('Model', filteredModels);
    }

    if (currentModel && filteredModels.includes(currentModel)) {
        modelDropdown.value = currentModel;
    }
}

document.getElementById("predict-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = {
        Make: document.getElementById("Make").value,
        Model: document.getElementById("Model").value,
        Condition: document.getElementById("Condition").value,
        Age: parseFloat(document.getElementById("Age").value) || 0,
        "Engine Size": parseFloat(document.getElementById("EngineSize").value) || 0,
        "Horse Power": parseFloat(document.getElementById("HorsePower").value) || 0
    };

    if (!formData.Make || !formData.Model || !formData.Condition) {
        document.getElementById("result").textContent = "Please select all options";
        return;
    }

    if (formData.Age <= 0 || formData["Engine Size"] <= 0 || formData["Horse Power"] <= 0) {
        document.getElementById("result").textContent = "Please enter valid numeric values";
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/predict`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById("result").textContent = `Estimated Price: ₦${data.predicted_price.toLocaleString()}`;
        } else {
            document.getElementById("result").textContent = `Error: ${data.error}`;
        }
    } catch (error) {
        document.getElementById("result").textContent = `Request failed: ${error}`;
    }
});