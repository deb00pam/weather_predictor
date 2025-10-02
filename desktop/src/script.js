import { invoke } from '@tauri-apps/api/tauri';

// DOM Elements
const backendStatus = document.getElementById('backend-status');
const statusText = document.getElementById('status-text');
const predictBtn = document.getElementById('predict-btn');
const resultsSection = document.getElementById('results-section');
const loadingSection = document.getElementById('loading');
const errorSection = document.getElementById('error');
const errorMessage = document.getElementById('error-message');

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
});

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
    
    // Form validation
    [temperatureInput, humidityInput, windSpeedInput, pressureInput].forEach(input => {
        input.addEventListener('input', validateForm);
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
    const temperature = parseFloat(temperatureInput.value);
    const humidity = parseFloat(humidityInput.value);
    const windSpeed = parseFloat(windSpeedInput.value);
    const pressure = parseFloat(pressureInput.value);
    
    const isValid = 
        !isNaN(temperature) && temperature >= -50 && temperature <= 60 &&
        !isNaN(humidity) && humidity >= 0 && humidity <= 100 &&
        !isNaN(windSpeed) && windSpeed >= 0 &&
        !isNaN(pressure) && pressure > 0;
    
    predictBtn.disabled = !isValid || backendStatus.className.includes('disconnected');
}

// Handle prediction request
async function handlePrediction() {
    hideAllSections();
    showLoading();
    
    try {
        const temperature = parseFloat(temperatureInput.value);
        const humidity = parseFloat(humidityInput.value);
        const windSpeed = parseFloat(windSpeedInput.value);
        const pressure = parseFloat(pressureInput.value);
        const activity = activitySelect.value;
        
        console.log('Making prediction request:', { temperature, humidity, windSpeed, pressure, activity });
        
        const result = await invoke('get_weather_prediction', {
            temperature,
            humidity,
            windSpeed,
            pressure,
            activity
        });
        
        console.log('Prediction result:', result);
        displayResults(result);
        
    } catch (error) {
        console.error('Prediction failed:', error);
        showError(`Prediction failed: ${error}`);
    }
}

// Display prediction results
function displayResults(result) {
    hideAllSections();
    
    // Update activity risk
    riskValue.textContent = result.activity_risk;
    riskValue.className = `risk-value ${result.activity_risk.toLowerCase()}`;
    
    // Update recommendation
    recText.textContent = result.recommendation;
    
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