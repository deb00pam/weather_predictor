// UI Manager for NASA Weather Risk Detection
class UIManager {
  constructor() {
    this.locationSuggestions = [];
    this.selectedLocation = null;
    this.isAnalyzing = false;
    
    this.initializeElements();
    this.bindEvents();
  }

  initializeElements() {
    // Form elements
    this.locationInput = document.getElementById('location-input');
    this.locationSuggestions = document.getElementById('location-suggestions');
    this.startDateInput = document.getElementById('start-date');
    this.endDateInput = document.getElementById('end-date');
    this.activitySelect = document.getElementById('activity-type');
    this.analyzeBtn = document.getElementById('analyze-btn');
    this.riskForm = document.getElementById('risk-form');

    // Result elements
    this.resultsPanel = document.getElementById('results-panel');
    this.resultLocation = document.getElementById('result-location');
    this.overallRisk = document.getElementById('overall-risk');
    this.riskScore = document.getElementById('risk-score');
    this.riskDescription = document.getElementById('risk-description');
    this.riskCategories = document.getElementById('risk-categories');
    this.recommendationsList = document.getElementById('recommendations-list');
    this.dataYears = document.getElementById('data-years');
    this.yearsCount = document.getElementById('years-count');

    // Status elements
    this.apiStatus = document.getElementById('api-status');
    this.apiStatusText = document.getElementById('api-status-text');
    this.loadingOverlay = document.getElementById('loading-overlay');
    this.loadingText = document.getElementById('loading-text');

    // Set default dates (today + 7 days)
    const today = new Date();
    const nextWeek = new Date();
    nextWeek.setDate(today.getDate() + 7);
    
    this.startDateInput.value = this.formatDateForInput(today);
    this.endDateInput.value = this.formatDateForInput(nextWeek);
  }

  bindEvents() {
    // Location search
    this.locationInput.addEventListener('input', this.debounce(this.handleLocationInput.bind(this), 300));
    this.locationInput.addEventListener('keydown', this.handleLocationKeydown.bind(this));
    document.getElementById('location-search-btn').addEventListener('click', this.handleLocationSearch.bind(this));

    // Form submission
    this.riskForm.addEventListener('submit', this.handleFormSubmit.bind(this));

    // Date validation
    this.startDateInput.addEventListener('change', this.validateDates.bind(this));
    this.endDateInput.addEventListener('change', this.validateDates.bind(this));

    // Chart toggle buttons
    document.getElementById('show-charts-btn').addEventListener('click', this.showCharts.bind(this));
    document.getElementById('hide-charts-btn').addEventListener('click', this.hideCharts.bind(this));

    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
      if (!this.locationInput.contains(e.target) && !this.locationSuggestions.contains(e.target)) {
        this.hideSuggestions();
      }
    });
  }

  // Utility function to debounce input
  debounce(func, wait) {
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

  // Format date for input field
  formatDateForInput(date) {
    return date.toISOString().split('T')[0];
  }

  // Handle location input changes
  async handleLocationInput(event) {
    const query = event.target.value.trim();
    
    if (query.length < 3) {
      this.hideSuggestions();
      return;
    }

    try {
      this.showLoadingInSuggestions();
      const locations = await weatherAPI.geocodeLocation(query);
      this.showLocationSuggestions(locations);
    } catch (error) {
      this.showErrorInSuggestions(error.message);
    }
  }

  // Handle location search button click
  async handleLocationSearch() {
    const query = this.locationInput.value.trim();
    if (!query) return;

    await this.handleLocationInput({ target: { value: query } });
  }

  // Handle keydown in location input
  handleLocationKeydown(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      this.handleLocationSearch();
    } else if (event.key === 'Escape') {
      this.hideSuggestions();
    }
  }

  // Show location suggestions
  showLocationSuggestions(locations) {
    this.locationSuggestions.innerHTML = '';
    
    if (locations.length === 0) {
      this.showErrorInSuggestions('No locations found');
      return;
    }

    locations.forEach(location => {
      const item = document.createElement('div');
      item.className = 'suggestion-item';
      item.innerHTML = `
        <div style="font-weight: 500;">${location.name}</div>
        <div style="font-size: 0.75rem; color: var(--text-muted);">
          ${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}
        </div>
      `;
      
      item.addEventListener('click', () => {
        this.selectLocation(location);
      });
      
      this.locationSuggestions.appendChild(item);
    });

    this.showSuggestions();
  }

  // Show loading in suggestions
  showLoadingInSuggestions() {
    this.locationSuggestions.innerHTML = `
      <div class="suggestion-item" style="color: var(--text-muted);">
        <i class="fas fa-spinner fa-spin"></i> Searching...
      </div>
    `;
    this.showSuggestions();
  }

  // Show error in suggestions
  showErrorInSuggestions(message) {
    this.locationSuggestions.innerHTML = `
      <div class="suggestion-item" style="color: var(--risk-high);">
        <i class="fas fa-exclamation-triangle"></i> ${message}
      </div>
    `;
    this.showSuggestions();
  }

  // Show suggestions dropdown
  showSuggestions() {
    this.locationSuggestions.style.display = 'block';
  }

  // Hide suggestions dropdown
  hideSuggestions() {
    this.locationSuggestions.style.display = 'none';
  }

  // Select a location from suggestions
  selectLocation(location) {
    this.selectedLocation = location;
    this.locationInput.value = location.name;
    this.hideSuggestions();
  }

  // Validate date range
  validateDates() {
    const startDate = new Date(this.startDateInput.value);
    const endDate = new Date(this.endDateInput.value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Check if start date is in the past
    if (startDate < today) {
      this.showNotification('Start date cannot be in the past', 'warning');
      this.startDateInput.value = this.formatDateForInput(today);
      return false;
    }

    // Check if end date is before start date
    if (endDate < startDate) {
      this.showNotification('End date must be after start date', 'warning');
      const nextDay = new Date(startDate);
      nextDay.setDate(startDate.getDate() + 1);
      this.endDateInput.value = this.formatDateForInput(nextDay);
      return false;
    }

    // Check if date range is too long (more than 30 days)
    const daysDiff = (endDate - startDate) / (1000 * 60 * 60 * 24);
    if (daysDiff > 30) {
      this.showNotification('Date range cannot exceed 30 days', 'warning');
      const maxEndDate = new Date(startDate);
      maxEndDate.setDate(startDate.getDate() + 30);
      this.endDateInput.value = this.formatDateForInput(maxEndDate);
      return false;
    }

    return true;
  }

  // Handle form submission
  async handleFormSubmit(event) {
    event.preventDefault();
    
    if (this.isAnalyzing) return;

    // Validate inputs
    if (!this.selectedLocation) {
      this.showNotification('Please select a location from the suggestions', 'error');
      return;
    }

    if (!this.validateDates()) {
      return;
    }

    try {
      this.setAnalyzing(true);
      this.showLoadingOverlay('Fetching NASA POWER data...');

      const startDate = this.startDateInput.value;
      const endDate = this.endDateInput.value;
      const activityType = this.activitySelect.value;

      const results = await weatherAPI.analyzeWeatherRisk(
        this.selectedLocation.latitude,
        this.selectedLocation.longitude,
        startDate,
        endDate,
        activityType
      );

      this.displayResults(results);
      this.showNotification('Weather risk analysis completed successfully!', 'success');

    } catch (error) {
      console.error('Analysis failed:', error);
      this.showNotification(error.message, 'error');
    } finally {
      this.setAnalyzing(false);
      this.hideLoadingOverlay();
    }
  }

  // Set analyzing state
  setAnalyzing(analyzing) {
    this.isAnalyzing = analyzing;
    this.analyzeBtn.disabled = analyzing;
    this.analyzeBtn.classList.toggle('loading', analyzing);
  }

  // Show loading overlay
  showLoadingOverlay(text = 'Loading...') {
    this.loadingText.textContent = text;
    this.loadingOverlay.classList.add('show');
  }

  // Hide loading overlay
  hideLoadingOverlay() {
    this.loadingOverlay.classList.remove('show');
  }

  // Display analysis results
  displayResults(results) {
    // Update location info
    this.resultLocation.innerHTML = `
      <i class="fas fa-map-marker-alt"></i>
      ${this.selectedLocation.name}
    `;

    // Update overall risk score
    const riskLevel = this.getRiskLevel(results.overall_risk_score);
    this.riskScore.textContent = `${results.overall_risk_score}%`;
    this.riskScore.className = `risk-score ${riskLevel}`;
    
    this.riskDescription.textContent = this.getRiskDescription(results.overall_risk_score);

    // Update risk categories
    this.displayRiskCategories(results.risk_categories);

    // Update recommendations
    this.displayRecommendations(results.recommendations);

    // Update data info
    this.yearsCount.textContent = results.historical_data_years;
    this.dataYears.style.display = 'block';

    // Show results panel
    this.resultsPanel.scrollIntoView({ behavior: 'smooth' });
  }

  // Display risk categories
  displayRiskCategories(categories) {
    this.riskCategories.innerHTML = '';

    categories.forEach(category => {
      const riskLevel = this.getRiskLevel(category.probability);
      const categoryElement = document.createElement('div');
      categoryElement.className = `risk-category ${riskLevel}`;
      
      categoryElement.innerHTML = `
        <div class="category-info">
          <div class="category-name">
            ${this.getCategoryIcon(category.category)}
            ${category.description}
          </div>
          <div class="category-description">
            ${category.activity_impact}
          </div>
        </div>
        <div class="category-stats">
          <div class="category-probability ${riskLevel}">
            ${category.probability}%
          </div>
          <div class="category-confidence">
            ${category.confidence}% confidence
          </div>
        </div>
      `;

      this.riskCategories.appendChild(categoryElement);
    });
  }

  // Display recommendations
  displayRecommendations(recommendations) {
    this.recommendationsList.innerHTML = '';

    recommendations.forEach(recommendation => {
      const listItem = document.createElement('li');
      listItem.textContent = recommendation;
      this.recommendationsList.appendChild(listItem);
    });
  }

  // Get risk level from probability
  getRiskLevel(probability) {
    if (probability >= 30) return 'very-high';
    if (probability >= 20) return 'high';
    if (probability >= 10) return 'moderate';
    return 'low';
  }

  // Get risk description
  getRiskDescription(riskScore) {
    if (riskScore >= 40) {
      return 'High overall weather risk detected. Consider postponing or relocating your activity.';
    } else if (riskScore >= 25) {
      return 'Moderate weather risk. Monitor conditions and prepare contingency plans.';
    } else if (riskScore >= 10) {
      return 'Low to moderate weather risk. Standard precautions recommended.';
    } else {
      return 'Low weather risk. Good conditions expected for outdoor activities.';
    }
  }

  // Get category icon
  getCategoryIcon(category) {
    const icons = {
      'very_hot': '<i class="fas fa-thermometer-full" style="color: var(--risk-high);"></i>',
      'very_cold': '<i class="fas fa-snowflake" style="color: var(--nasa-light-blue);"></i>',
      'very_windy': '<i class="fas fa-wind" style="color: var(--risk-moderate);"></i>',
      'very_wet': '<i class="fas fa-cloud-rain" style="color: var(--nasa-blue);"></i>',
      'very_uncomfortable': '<i class="fas fa-temperature-high" style="color: var(--nasa-red);"></i>'
    };
    return icons[category] || '<i class="fas fa-exclamation-triangle"></i>';
  }

  // Show notification
  showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <i class="fas fa-${this.getNotificationIcon(type)}"></i>
        <span>${message}</span>
      </div>
    `;

    // Add styles
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: var(--surface);
      border: 2px solid ${this.getNotificationColor(type)};
      border-radius: var(--radius-lg);
      padding: var(--spacing-md) var(--spacing-lg);
      box-shadow: var(--shadow-lg);
      z-index: 1001;
      max-width: 400px;
      animation: slideIn 0.3s ease;
    `;

    // Add notification to DOM
    document.body.appendChild(notification);

    // Remove after 5 seconds
    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 5000);
  }

  // Get notification icon
  getNotificationIcon(type) {
    const icons = {
      'success': 'check-circle',
      'error': 'exclamation-circle',
      'warning': 'exclamation-triangle',
      'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
  }

  // Get notification color
  getNotificationColor(type) {
    const colors = {
      'success': 'var(--risk-low)',
      'error': 'var(--risk-high)',
      'warning': 'var(--risk-moderate)',
      'info': 'var(--primary-color)'
    };
    return colors[type] || 'var(--primary-color)';
  }

  // Update API status
  updateAPIStatus(status, message) {
    this.apiStatusText.textContent = message;
    this.apiStatus.className = `status-indicator ${status}`;
  }

  // Chart toggle methods
  showCharts() {
    const chartsSection = document.getElementById('charts-section');
    const showChartsSection = document.getElementById('show-charts-section');
    
    chartsSection.style.display = 'block';
    showChartsSection.style.display = 'none';

    // Trigger chart creation if we have data
    if (window.chartManager && window.lastAnalysisResults) {
      chartManager.updateCharts(window.lastAnalysisResults);
    }
  }

  hideCharts() {
    const chartsSection = document.getElementById('charts-section');
    const showChartsSection = document.getElementById('show-charts-section');
    
    chartsSection.style.display = 'none';
    showChartsSection.style.display = 'block';

    // Clear charts to free memory
    if (window.chartManager) {
      chartManager.clearCharts();
    }
  }
}

// Add notification animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }

  .notification-content {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
  }
`;
document.head.appendChild(style);

// Create global UI instance
window.uiManager = new UIManager();