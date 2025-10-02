import { invoke } from '@tauri-apps/api/tauri';

// DOM Elements
const backendStatus = document.getElementById('backend-status');
const statusText = document.getElementById('status-text');
const predictBtn = document.getElementById('predict-btn');
const resultsSection = document.getElementById('results-section');
const loadingSection = document.getElementById('loading');
const errorSection = document.getElementById('error');
const errorMessage = document.getElementById('error-message');

// Query elements
const queryDate = document.getElementById('query-date');
const locationInput = document.getElementById('location-input');
const latitudeInput = document.getElementById('latitude');
const longitudeInput = document.getElementById('longitude');
const autoQueryBtn = document.getElementById('auto-query-btn');
const manualModeBtn = document.getElementById('manual-mode-btn');
const querySections = {
    query: document.querySelector('.query-section'),
    manual: document.querySelector('.manual-section')
};
const coordsGroups = document.querySelectorAll('.coords-group');

// Form elements
const temperatureInput = document.getElementById('temperature');
const humidityInput = document.getElementById('humidity');
const windSpeedInput = document.getElementById('wind-speed');
const pressureInput = document.getElementById('pressure');
const activitySelect = document.getElementById('activity');

// Result elements
const activityRisk = document.getElementById('activity-risk');
const riskValue = document.getElementById('risk-value');
const recText = document.getElementById('rec-text');

// Prediction value elements
const predictionElements = {
    'very_hot': {
        value: document.getElementById('very-hot'),
        fill: document.getElementById('very-hot-fill')
    },
    'very_cold': {
        value: document.getElementById('very-cold'),
        fill: document.getElementById('very-cold-fill')
    },
    'very_windy': {
        value: document.getElementById('very-windy'),
        fill: document.getElementById('very-windy-fill')
    },
    'very_wet': {
        value: document.getElementById('very-wet'),
        fill: document.getElementById('very-wet-fill')
    },
    'very_uncomfortable': {
        value: document.getElementById('very-uncomfortable'),
        fill: document.getElementById('very-uncomfortable-fill')
    }
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    checkBackendHealth();
    setupEventListeners();
    loadSampleData();
    initializeDatePicker();
    setupQueryMode();
});

// Initialize date picker with tomorrow as default
function initializeDatePicker() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    queryDate.value = tomorrow.toISOString().split('T')[0];
}

// Setup query mode toggle
function setupQueryMode() {
    autoQueryBtn.addEventListener('click', () => switchToQueryMode());
    manualModeBtn.addEventListener('click', () => switchToManualMode());
    
    // Location input handling
    locationInput.addEventListener('input', handleLocationInput);
    latitudeInput.addEventListener('input', validateForm);
    longitudeInput.addEventListener('input', validateForm);
}

function switchToQueryMode() {
    autoQueryBtn.classList.add('active');
    manualModeBtn.classList.remove('active');
    querySections.manual.style.display = 'none';
    
    // Update button text
    predictBtn.textContent = 'Get Weather Prediction for Location & Date';
}

function switchToManualMode() {
    manualModeBtn.classList.add('active');
    autoQueryBtn.classList.remove('active');
    querySections.manual.style.display = 'block';
    
    // Update button text
    predictBtn.textContent = 'Get Weather Prediction';
}

function handleLocationInput() {
    const input = locationInput.value.trim();
    
    // Check if input looks like coordinates (lat,lon)
    const coordPattern = /^-?\d+\.?\d*\s*,\s*-?\d+\.?\d*$/;
    
    if (coordPattern.test(input)) {
        const [lat, lon] = input.split(',').map(coord => parseFloat(coord.trim()));
        latitudeInput.value = lat;
        longitudeInput.value = lon;
        coordsGroups.forEach(group => group.style.display = 'block');
    } else {
        coordsGroups.forEach(group => group.style.display = 'none');
    }
    
    validateForm();
}

// Check backend connection
async function checkBackendHealth() {
    try {
        const result = await invoke('check_backend_health');
        statusText.textContent = result;
        backendStatus.className = 'status-indicator connected';
        predictBtn.disabled = false;
    } catch (error) {
        statusText.textContent = 'Backend disconnected - Please start Python server';
        backendStatus.className = 'status-indicator disconnected';
        predictBtn.disabled = true;
        console.error('Backend health check failed:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    predictBtn.addEventListener('click', handlePrediction);
    
    // Auto-check backend health periodically
    setInterval(checkBackendHealth, 30000); // Check every 30 seconds
    
    // Form validation - manual mode
    [temperatureInput, humidityInput, windSpeedInput, pressureInput].forEach(input => {
        input.addEventListener('input', validateForm);
    });
    
    // Form validation - query mode
    [queryDate, locationInput, latitudeInput, longitudeInput, activitySelect].forEach(input => {
        input.addEventListener('input', validateForm);
        input.addEventListener('change', validateForm);
    });
}

// Load sample data for testing
function loadSampleData() {
    temperatureInput.value = '25';
    humidityInput.value = '65';
    windSpeedInput.value = '12';
    pressureInput.value = '1013';
    activitySelect.value = 'hiking';
}

// Validate form inputs
function validateForm() {
    const isAutoMode = autoQueryBtn.classList.contains('active');
    let isValid = false;
    
    if (isAutoMode) {
        // Validate query mode - need date and location
        const hasDate = queryDate.value !== '';
        const hasLocation = locationInput.value.trim() !== '' || 
                           (latitudeInput.value !== '' && longitudeInput.value !== '');
        const hasActivity = activitySelect.value !== '';
        
        isValid = hasDate && hasLocation && hasActivity;
    } else {
        // Validate manual mode - need all weather parameters
        const temperature = parseFloat(temperatureInput.value);
        const humidity = parseFloat(humidityInput.value);
        const windSpeed = parseFloat(windSpeedInput.value);
        const pressure = parseFloat(pressureInput.value);
        
        isValid = 
            !isNaN(temperature) && temperature >= -50 && temperature <= 60 &&
            !isNaN(humidity) && humidity >= 0 && humidity <= 100 &&
            !isNaN(windSpeed) && windSpeed >= 0 &&
            !isNaN(pressure) && pressure > 0 &&
            activitySelect.value !== '';
    }
    
    predictBtn.disabled = !isValid || backendStatus.className.includes('disconnected');
}

// Handle prediction request
async function handlePrediction() {
    hideAllSections();
    showLoading();
    
    try {
        const isAutoMode = autoQueryBtn.classList.contains('active');
        const activity = activitySelect.value;
        
        if (isAutoMode) {
            // Query mode - use location and date
            await handleLocationQuery(activity);
        } else {
            // Manual mode - use direct weather parameters
            await handleManualPrediction(activity);
        }
        
    } catch (error) {
        console.error('Prediction failed:', error);
        showError(`Prediction failed: ${error}`);
    }
}

async function handleLocationQuery(activity) {
    // Get location coordinates
    let lat, lon;
    
    if (latitudeInput.value && longitudeInput.value) {
        lat = parseFloat(latitudeInput.value);
        lon = parseFloat(longitudeInput.value);
    } else {
        // In a real app, we'd geocode the location name
        // For now, use a default location
        lat = 40.7128; // New York City
        lon = -74.0060;
        console.warn('Using default coordinates for:', locationInput.value);
    }
    
    const dateStr = queryDate.value;
    
    console.log('Making location-based query:', { dateStr, lat, lon, activity });
    
    // Use the simple GET endpoint for location queries
    const response = await fetch(`http://localhost:8000/predict-weather-simple?date_str=${dateStr}&lat=${lat}&lon=${lon}&activity=${activity}`);
    
    if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('Location query result:', result);
    
    // Transform the response to match our display format
    const displayResult = {
        prediction: result.prediction.conditions,
        activity_risk: result.prediction.risk_level,
        recommendation: result.prediction.recommendations.join(' '),
        timestamp: new Date().toISOString(),
        location_info: `${locationInput.value || 'Custom Location'} (${lat.toFixed(4)}, ${lon.toFixed(4)})`,
        query_date: dateStr
    };
    
    displayResults(displayResult);
}

async function handleManualPrediction(activity) {
    const temperature = parseFloat(temperatureInput.value);
    const humidity = parseFloat(humidityInput.value);
    const windSpeed = parseFloat(windSpeedInput.value);
    const pressure = parseFloat(pressureInput.value);
    
    console.log('Making manual prediction request:', { temperature, humidity, windSpeed, pressure, activity });
    
    const result = await invoke('get_weather_prediction', {
        temperature,
        humidity,
        windSpeed,
        pressure,
        activity
    });
    
    console.log('Manual prediction result:', result);
    displayResults(result);
}

// Display prediction results
function displayResults(result) {
    hideAllSections();
    
    // Update activity risk
    riskValue.textContent = result.activity_risk;
    riskValue.className = `risk-value ${result.activity_risk.toLowerCase()}`;
    
    // Update recommendation
    let recommendationText = result.recommendation;
    
    // Add location and date info if available
    if (result.location_info) {
        recommendationText = `📍 ${result.location_info} | 📅 ${result.query_date}\n\n${recommendationText}`;
    }
    
    recText.textContent = recommendationText;
    
    // Update prediction values and bars
    const predictions = result.prediction;
    Object.keys(predictions).forEach(key => {
        if (predictionElements[key]) {
            const percentage = Math.round(predictions[key] * 100);
            predictionElements[key].value.textContent = `${percentage}%`;
            predictionElements[key].fill.style.width = `${percentage}%`;
            
            // Set color based on risk level
            const fillElement = predictionElements[key].fill;
            if (percentage > 70) {
                fillElement.className = 'prediction-fill high';
            } else if (percentage > 40) {
                fillElement.className = 'prediction-fill medium';
            } else {
                fillElement.className = 'prediction-fill';
            }
        }
    });
    
    resultsSection.style.display = 'block';
}

// Show loading state
function showLoading() {
    loadingSection.style.display = 'block';
}

// Show error message
function showError(message) {
    hideAllSections();
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
}

// Hide all result sections
function hideAllSections() {
    resultsSection.style.display = 'none';
    loadingSection.style.display = 'none';
    errorSection.style.display = 'none';
}

// Export functions for debugging
window.weatherApp = {
    checkBackendHealth,
    handlePrediction,
    loadSampleData
};