// DOM Elements (will be initialized after DOM loads)
let predictBtn, resultsSection, loadingSection, errorSection, errorMessage;
let queryDate, locationInput, activitySelect;
let customThresholdControls, temperatureRange, windSpeedRange, humidityRange, cloudCoverRange, precipitationRange;
let thresholdToggle, locationCompareSection, comparisonResults, primaryLocationInput, secondaryLocationInput;
let compareLocationBtn, dateRangeSection, startDateInput, endDateInput, analyzeDateRangeBtn, dateRangeResults;

// Global configuration and state
const BACKEND_BASE_URL = 'http://localhost:8000';
const customThresholds = {
    temperature: { min: -20, max: 45 },
    windSpeed: { min: 0, max: 25 },
    humidity: { min: 30, max: 80 },
    cloudCover: { min: 0, max: 70 },
    precipitation: { min: 0, max: 5 }
};

// Cache for geocoded locations to avoid repeated API calls
const locationCache = new Map();

// Popular locations for quick suggestions (optional fallback)
const POPULAR_LOCATIONS = [
    'New York, USA', 'London, UK', 'Tokyo, Japan', 'Sydney, Australia',
    'Paris, France', 'Berlin, Germany', 'Moscow, Russia', 'Beijing, China',
    'Mumbai, India', 'Cairo, Egypt', 'Cape Town, South Africa', 'Rio de Janeiro, Brazil',
    'Mexico City, Mexico', 'Toronto, Canada', 'Los Angeles, USA', 'Chicago, USA'
];

// Backend geocoding function using our API
async function geocodeLocation(locationString) {
    // Check cache first
    if (locationCache.has(locationString)) {
        return locationCache.get(locationString);
    }
    
    try {
        const response = await fetch(`${BACKEND_BASE_URL}/geocode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ location: locationString })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            const result = {
                lat: data.latitude,
                lon: data.longitude,
                name: data.display_name,
                country: data.country,
                city: data.city
            };
            
            // Cache the result
            locationCache.set(locationString, result);
            return result;
        } else {
            console.error('Geocoding failed:', data.error);
            return null;
        }
        
    } catch (error) {
        console.error('Geocoding error:', error);
        return null;
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();

    setupEventListeners();
    initializeCustomThresholds();
    updateThresholdDisplay();
});

function initializeElements() {
    // Status elements

    
    // Form elements
    predictBtn = document.getElementById('predict-btn');
    queryDate = document.getElementById('query-date');
    locationInput = document.getElementById('location-input');

    activitySelect = document.getElementById('activity');
    
    // Results elements
    resultsSection = document.getElementById('results-section');
    loadingSection = document.getElementById('loading');
    errorSection = document.getElementById('error');
    errorMessage = document.getElementById('error-message');
    
    // Custom threshold elements
    customThresholdControls = document.getElementById('custom-threshold-controls');
    temperatureRange = document.getElementById('temperature-range');
    windSpeedRange = document.getElementById('wind-speed-range');
    humidityRange = document.getElementById('humidity-range');
    cloudCoverRange = document.getElementById('cloud-cover-range');
    precipitationRange = document.getElementById('precipitation-range');
    thresholdToggle = document.getElementById('threshold-toggle');
    
    // Location comparison elements
    locationCompareSection = document.getElementById('location-compare-section');
    comparisonResults = document.getElementById('comparison-results');
    primaryLocationInput = document.getElementById('primary-location');
    secondaryLocationInput = document.getElementById('secondary-location');
    compareLocationBtn = document.getElementById('compare-locations-btn');
    
    // Date range analysis elements
    dateRangeSection = document.getElementById('date-range-section');
    startDateInput = document.getElementById('start-date');
    endDateInput = document.getElementById('end-date');
    analyzeDateRangeBtn = document.getElementById('analyze-date-range-btn');
    dateRangeResults = document.getElementById('date-range-results');
    
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    if (queryDate) queryDate.value = today;
    if (startDateInput) startDateInput.value = today;
    if (endDateInput) {
        const nextWeek = new Date();
        nextWeek.setDate(nextWeek.getDate() + 7);
        endDateInput.value = nextWeek.toISOString().split('T')[0];
    }
}

function setupEventListeners() {
    // Prediction button
    if (predictBtn) {
        predictBtn.addEventListener('click', handlePrediction);
    }
    
    // Mode buttons

    
    // Custom threshold toggle
    if (thresholdToggle) {
        thresholdToggle.addEventListener('change', toggleCustomThresholds);
    }
    
    // Threshold range inputs
    const thresholdInputs = [temperatureRange, windSpeedRange, humidityRange, cloudCoverRange, precipitationRange];
    thresholdInputs.forEach(input => {
        if (input) {
            input.addEventListener('input', updateThresholdValues);
        }
    });
    
    // Location comparison
    if (compareLocationBtn) {
        compareLocationBtn.addEventListener('click', compareLocations);
    }
    
    // Date range analysis
    if (analyzeDateRangeBtn) {
        analyzeDateRangeBtn.addEventListener('click', analyzeDateRange);
    }
    
    // Auto-complete for location inputs
    setupLocationAutocomplete();
}

function setupLocationAutocomplete() {
    const locationInputs = [locationInput, primaryLocationInput, secondaryLocationInput];
    
    locationInputs.forEach(input => {
        if (input) {
            let autocompleteTimeout;
            
            input.addEventListener('input', function() {
                const value = this.value.trim();
                
                // Clear previous timeout
                if (autocompleteTimeout) {
                    clearTimeout(autocompleteTimeout);
                }
                
                // Show popular suggestions for short queries
                if (value.length > 1 && value.length < 4) {
                    const matches = POPULAR_LOCATIONS.filter(location => 
                        location.toLowerCase().includes(value.toLowerCase())
                    );
                    
                    if (matches.length > 0) {
                        this.setAttribute('placeholder', matches[0]);
                    }
                }
                
                // For longer queries, we could implement a dropdown with OpenStreetMap suggestions
                // This would require additional UI components
            });
            
            // Add a "Find Location" button next to input
            if (!input.nextElementSibling || !input.nextElementSibling.classList.contains('find-location-btn')) {
                const findBtn = document.createElement('button');
                findBtn.type = 'button';
                findBtn.className = 'find-location-btn';
                findBtn.textContent = '🌍 Find';
                findBtn.title = 'Find this location on the map';
                
                findBtn.addEventListener('click', async () => {
                    const locationString = input.value.trim();
                    if (locationString) {
                        try {
                            input.disabled = true;
                            findBtn.textContent = '⏳ Finding...';
                            
                            const coords = await geocodeLocation(locationString);
                            if (coords) {
                                input.value = coords.name || locationString;
                                input.dataset.lat = coords.lat;
                                input.dataset.lon = coords.lon;
                                findBtn.textContent = '✅ Found';
                                setTimeout(() => {
                                    findBtn.textContent = '🌍 Find';
                                }, 2000);
                            } else {
                                findBtn.textContent = '❌ Not Found';
                                setTimeout(() => {
                                    findBtn.textContent = '🌍 Find';
                                }, 2000);
                            }
                        } catch (error) {
                            console.error('Location search failed:', error);
                            findBtn.textContent = '❌ Error';
                            setTimeout(() => {
                                findBtn.textContent = '🌍 Find';
                            }, 2000);
                        } finally {
                            input.disabled = false;
                        }
                    }
                });
                
                input.parentNode.style.position = 'relative';
                input.parentNode.appendChild(findBtn);
            }
        }
    });
}



function toggleMode(mode) {
    // Always keep auto button active since it's the only option

}

function initializeCustomThresholds() {
    Object.assign(customThresholds, {
        temperature: { min: -20, max: 45 },
        windSpeed: { min: 0, max: 25 },
        humidity: { min: 30, max: 80 },
        cloudCover: { min: 0, max: 70 },
        precipitation: { min: 0, max: 5 }
    });
}

function toggleCustomThresholds() {
    if (customThresholdControls && thresholdToggle) {
        customThresholdControls.style.display = thresholdToggle.checked ? 'block' : 'none';
    }
}

function updateThresholdValues() {
    const ranges = {
        temperature: temperatureRange,
        windSpeed: windSpeedRange,
        humidity: humidityRange,
        cloudCover: cloudCoverRange,
        precipitation: precipitationRange
    };
    
    Object.keys(ranges).forEach(key => {
        const range = ranges[key];
        if (range) {
            const values = range.value.split(',');
            customThresholds[key] = {
                min: parseFloat(values[0]),
                max: parseFloat(values[1])
            };
        }
    });
    
    updateThresholdDisplay();
}

function updateThresholdDisplay() {
    const displays = {
        'temperature-display': customThresholds.temperature,
        'wind-speed-display': customThresholds.windSpeed,
        'humidity-display': customThresholds.humidity,
        'cloud-cover-display': customThresholds.cloudCover,
        'precipitation-display': customThresholds.precipitation
    };
    
    Object.keys(displays).forEach(id => {
        const element = document.getElementById(id);
        const threshold = displays[id];
        if (element && threshold) {
            element.textContent = `${threshold.min} - ${threshold.max}`;
        }
    });
}

async function handlePrediction() {
    hideAllSections();
    showSection(loadingSection);
    
    try {
        const formData = await collectFormData();
        if (!formData) return;
        
        // Debug: Log the data being sent
        console.log('Sending data to backend:', JSON.stringify(formData, null, 2));
        
        const endpoint = determineEndpoint();
        const response = await fetch(`${BACKEND_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('Parsed JSON result:', result);
        displayResults(result);
        
    } catch (error) {
        console.error('Prediction failed:', error);
        showError(`Prediction failed: ${error.message}`);
    }
}

async function collectFormData() {
    const location = locationInput?.value?.trim();
    if (!location) {
        showError('Please enter a location.');
        return null;
    }
    
    let lat, lon;
    
    // Check if coordinates are already cached in the input element
    if (locationInput.dataset.lat && locationInput.dataset.lon) {
        lat = parseFloat(locationInput.dataset.lat);
        lon = parseFloat(locationInput.dataset.lon);
    } else {
        // Geocode the location using OpenStreetMap
        try {
            showSection(loadingSection);
            const coords = await geocodeLocation(location);
            
            if (!coords) {
                showError(`Location "${location}" not found. Please try a more specific address or city name.`);
                return null;
            }
            
            lat = coords.lat;
            lon = coords.lon;
            
            // Cache coordinates in the input element
            locationInput.dataset.lat = lat;
            locationInput.dataset.lon = lon;
            
        } catch (error) {
            showError(`Failed to find location: ${error.message}`);
            return null;
        }
    }
    
    const date = queryDate?.value;
    if (!date) {
        showError('Please select a query date.');
        return null;
    }
    
    // Get selected activity and map to backend values
    const selectedActivity = activitySelect?.value || 'hiking';
    const activityMapping = {
        'hiking': 'hiking',
        'fishing': 'fishing', 
        'vacation': 'beach_vacation',  // Map vacation to beach_vacation
        'camping': 'hiking',  // Map camping to hiking since no specific camping profile
        'cycling': 'hiking',  // Map cycling to hiking
        'outdoor_sports': 'hiking'  // Map outdoor sports to hiking
    };
    const activity = activityMapping[selectedActivity] || 'hiking';
    
    const formData = {
        date: date,  // Keep as string, backend will parse it
        location: {
            latitude: lat,
            longitude: lon,
            location_name: location  // Add the original location name
        },
        activity: activity
    };
    
    // Add custom thresholds if enabled
    if (thresholdToggle && thresholdToggle.checked) {
        formData.custom_thresholds = customThresholds;
    }
    
    return formData;
}

function determineEndpoint() {
    // Use the predict-weather endpoint that accepts coordinates
    return '/predict-weather';
}

function displayResults(data) {
    hideAllSections();
    
    console.log('Backend response:', data);
    
    if (!data || !data.prediction) {
        showError('Invalid response from server');
        return;
    }
    
    const prediction = data.prediction;
    const location = data.location || {};
    
    // Update risk overview
    const riskValueElement = document.getElementById('risk-value');
    if (riskValueElement) {
        riskValueElement.textContent = prediction.risk_level || 'moderate';
        riskValueElement.className = `risk-value risk-${prediction.risk_level || 'moderate'}`;
    }
    
    // Update recommendations
    const recTextElement = document.getElementById('rec-text');
    if (recTextElement && prediction.recommendations && prediction.recommendations.length > 0) {
        recTextElement.textContent = prediction.recommendations[0] || 'No specific recommendations';
    }
    
    // Update weather conditions with the correct structure
    const conditions = prediction.conditions || {};
    
    // Update each prediction card
    if (conditions.very_hot) {
        updatePredictionCard('very-hot', conditions.very_hot.probability * 100);
    }
    if (conditions.very_cold) {
        updatePredictionCard('very-cold', conditions.very_cold.probability * 100);
    }
    if (conditions.very_windy) {
        updatePredictionCard('very-windy', conditions.very_windy.probability * 100);
    }
    if (conditions.very_wet) {
        updatePredictionCard('very-wet', conditions.very_wet.probability * 100);
    }
    if (conditions.very_uncomfortable) {
        updatePredictionCard('very-uncomfortable', conditions.very_uncomfortable.probability * 100);
    }
    
    showSection(resultsSection);
}

function updatePredictionCard(conditionId, percentage) {
    const valueElement = document.getElementById(conditionId);
    const fillElement = document.getElementById(`${conditionId}-fill`);
    
    if (valueElement) {
        valueElement.textContent = `${percentage.toFixed(1)}%`;
    }
    
    if (fillElement) {
        fillElement.style.width = `${percentage}%`;
        
        // Add color coding based on percentage
        if (percentage >= 70) {
            fillElement.style.backgroundColor = '#e74c3c'; // Red for high risk
        } else if (percentage >= 40) {
            fillElement.style.backgroundColor = '#f39c12'; // Orange for moderate risk
        } else {
            fillElement.style.backgroundColor = '#27ae60'; // Green for low risk
        }
    }
}

function updateWeatherCondition(type, value, unit) {
    const valueElement = document.getElementById(`${type}-value`);
    const statusElement = document.getElementById(`${type}-status`);
    
    if (valueElement) {
        valueElement.textContent = `${value?.toFixed(1) || 'N/A'}${unit}`;
    }
    
    if (statusElement) {
        let status = 'moderate';
        let className = 'condition-moderate';
        
        const thresholdKey = type.includes('-') ? type.replace('-', '') : type;
        if (thresholdToggle && thresholdToggle.checked && customThresholds[thresholdKey]) {
            const threshold = customThresholds[thresholdKey];
            if (value < threshold.min || value > threshold.max) {
                status = 'poor';
                className = 'condition-poor';
            } else {
                status = 'good';
                className = 'condition-good';
            }
        } else {
            // Default thresholds
            const thresholds = {
                'temperature': { min: 10, max: 30 },
                'wind-speed': { min: 0, max: 15 },
                'humidity': { min: 40, max: 70 },
                'cloud-cover': { min: 0, max: 50 },
                'precipitation': { min: 0, max: 2 }
            };
            
            const threshold = thresholds[type];
            if (threshold) {
                if (value < threshold.min || value > threshold.max) {
                    status = 'poor';
                    className = 'condition-poor';
                } else {
                    status = 'good';
                    className = 'condition-good';
                }
            }
        }
        
        statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        statusElement.className = `condition-status ${className}`;
    }
}

function updateRecommendations(recommendations) {
    const container = document.getElementById('recommendations-list');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (recommendations.length === 0) {
        container.innerHTML = '<li>No specific recommendations available</li>';
        return;
    }
    
    recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = rec;
        container.appendChild(li);
    });
}

function updateRiskAssessment(assessment) {
    const levelElement = document.getElementById('risk-level');
    const summaryElement = document.getElementById('risk-summary');
    
    if (levelElement) {
        const level = assessment.level || 'moderate';
        levelElement.textContent = level.charAt(0).toUpperCase() + level.slice(1);
        levelElement.className = `risk-level risk-${level}`;
    }
    
    if (summaryElement) {
        summaryElement.textContent = assessment.summary || 'Standard weather conditions expected.';
    }
}

async function compareLocations() {
    const primaryLocation = primaryLocationInput?.value?.trim();
    const secondaryLocation = secondaryLocationInput?.value?.trim();
    
    if (!primaryLocation || !secondaryLocation) {
        showError('Please enter both locations for comparison.');
        return;
    }
    
    try {
        // Geocode both locations
        const [primaryCoords, secondaryCoords] = await Promise.all([
            primaryLocationInput.dataset.lat && primaryLocationInput.dataset.lon ?
                { lat: parseFloat(primaryLocationInput.dataset.lat), lon: parseFloat(primaryLocationInput.dataset.lon) } :
                geocodeLocation(primaryLocation),
            secondaryLocationInput.dataset.lat && secondaryLocationInput.dataset.lon ?
                { lat: parseFloat(secondaryLocationInput.dataset.lat), lon: parseFloat(secondaryLocationInput.dataset.lon) } :
                geocodeLocation(secondaryLocation)
        ]);
        
        if (!primaryCoords || !secondaryCoords) {
            showError('One or both locations could not be found. Please check the location names.');
            return;
        }
        const date = queryDate?.value || new Date().toISOString().split('T')[0];
        const selectedActivity = activitySelect?.value || 'hiking';
        const activityMapping = {
            'hiking': 'hiking',
            'fishing': 'fishing', 
            'vacation': 'beach_vacation',
            'camping': 'hiking',
            'cycling': 'hiking',
            'outdoor_sports': 'hiking'
        };
        const activity = activityMapping[selectedActivity] || 'hiking';
        
        const [primaryResponse, secondaryResponse] = await Promise.all([
            fetch(`${BACKEND_BASE_URL}/predict-weather`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    date: date,
                    location: {
                        latitude: primaryCoords.lat,
                        longitude: primaryCoords.lon
                    },
                    activity: activity
                })
            }),
            fetch(`${BACKEND_BASE_URL}/predict-weather`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    date: date,
                    location: {
                        latitude: secondaryCoords.lat,
                        longitude: secondaryCoords.lon
                    },
                    activity: activity
                })
            })
        ]);
        
        const primaryData = await primaryResponse.json();
        const secondaryData = await secondaryResponse.json();
        
        displayLocationComparison(primaryData, secondaryData, primaryLocation, secondaryLocation);
        
    } catch (error) {
        console.error('Location comparison failed:', error);
        showError(`Location comparison failed: ${error.message}`);
    }
}

function displayLocationComparison(primary, secondary, primaryName, secondaryName) {
    if (!comparisonResults) return;
    
    const html = `
        <h3>Location Comparison Results</h3>
        <div class="comparison-grid">
            <div class="comparison-location">
                <h4>${primaryName.charAt(0).toUpperCase() + primaryName.slice(1)}</h4>
                <div class="comparison-metrics">
                    <div>Temperature: ${primary.predictions?.temperature?.toFixed(1) || 'N/A'}°C</div>
                    <div>Wind Speed: ${primary.predictions?.wind_speed?.toFixed(1) || 'N/A'} km/h</div>
                    <div>Humidity: ${primary.predictions?.humidity?.toFixed(1) || 'N/A'}%</div>
                    <div>Risk Level: ${primary.risk_assessment?.level || 'moderate'}</div>
                </div>
            </div>
            <div class="comparison-location">
                <h4>${secondaryName.charAt(0).toUpperCase() + secondaryName.slice(1)}</h4>
                <div class="comparison-metrics">
                    <div>Temperature: ${secondary.predictions?.temperature?.toFixed(1) || 'N/A'}°C</div>
                    <div>Wind Speed: ${secondary.predictions?.wind_speed?.toFixed(1) || 'N/A'} km/h</div>
                    <div>Humidity: ${secondary.predictions?.humidity?.toFixed(1) || 'N/A'}%</div>
                    <div>Risk Level: ${secondary.risk_assessment?.level || 'moderate'}</div>
                </div>
            </div>
        </div>
    `;
    
    comparisonResults.innerHTML = html;
    comparisonResults.style.display = 'block';
}

async function analyzeDateRange() {
    const startDate = startDateInput?.value;
    const endDate = endDateInput?.value;
    
    if (!startDate || !endDate) {
        showError('Please select both start and end dates.');
        return;
    }
    
    const location = locationInput?.value?.trim();
    if (!location) {
        showError('Please enter a location for date range analysis.');
        return;
    }
    
    try {
        let coords;
        
        // Check if coordinates are already cached
        if (locationInput.dataset.lat && locationInput.dataset.lon) {
            coords = {
                lat: parseFloat(locationInput.dataset.lat),
                lon: parseFloat(locationInput.dataset.lon)
            };
        } else {
            coords = await geocodeLocation(location);
            if (!coords) {
                showError(`Location "${location}" not found.`);
                return;
            }
        }
        const response = await fetch(`${BACKEND_BASE_URL}/date-range-analysis`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                latitude: coords.lat,
                longitude: coords.lon,
                start_date: startDate,
                end_date: endDate
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        displayDateRangeAnalysis(data);
        
    } catch (error) {
        console.error('Date range analysis failed:', error);
        showError(`Date range analysis failed: ${error.message}`);
    }
}

function displayDateRangeAnalysis(data) {
    if (!dateRangeResults) return;
    
    const html = `
        <h3>Date Range Analysis Results</h3>
        <div class="date-range-summary">
            <h4>Summary (${data.start_date} to ${data.end_date})</h4>
            <div class="range-metrics">
                <div>Average Temperature: ${data.summary?.avg_temperature?.toFixed(1) || 'N/A'}°C</div>
                <div>Average Wind Speed: ${data.summary?.avg_wind_speed?.toFixed(1) || 'N/A'} km/h</div>
                <div>Average Humidity: ${data.summary?.avg_humidity?.toFixed(1) || 'N/A'}%</div>
                <div>Total Precipitation: ${data.summary?.total_precipitation?.toFixed(1) || 'N/A'} mm</div>
                <div>Best Day: ${data.summary?.best_day || 'N/A'}</div>
                <div>Worst Day: ${data.summary?.worst_day || 'N/A'}</div>
            </div>
        </div>
    `;
    
    dateRangeResults.innerHTML = html;
    dateRangeResults.style.display = 'block';
}

function hideAllSections() {
    const sections = [resultsSection, loadingSection, errorSection];
    sections.forEach(section => {
        if (section) section.style.display = 'none';
    });
}

function showSection(section) {
    if (section) section.style.display = 'block';
}

function showError(message) {
    hideAllSections();
    if (errorMessage) errorMessage.textContent = message;
    showSection(errorSection);
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        POPULAR_LOCATIONS,
        geocodeLocation,
        reverseGeocode,
        customThresholds,
        collectFormData,
        updateWeatherCondition
    };
}