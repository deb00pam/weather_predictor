// Main Application Controller for NASA Weather Risk Detection
class WeatherRiskApp {
  constructor() {
    this.isInitialized = false;
    this.init();
  }

  async init() {
    try {
      console.log('🚀 Initializing NASA Weather Risk Detection App...');
      
      // Show loading overlay
      uiManager.showLoadingOverlay('Initializing application...');
      
      // Check API connection
      await this.checkAPIConnection();
      
      // Initialize charts after a short delay to ensure DOM is ready
      setTimeout(() => {
        if (window.chartManager) {
          console.log('📊 Chart manager initialized');
        }
      }, 500);
      
      // Set up menu handlers if in Electron
      this.setupElectronHandlers();
      
      // Mark as initialized
      this.isInitialized = true;
      
      console.log('✅ Application initialized successfully');
      
      // Hide loading overlay
      uiManager.hideLoadingOverlay();
      
      // Show welcome message
      uiManager.showNotification('NASA Weather Risk Detection ready!', 'success');
      
    } catch (error) {
      console.error('❌ Failed to initialize application:', error);
      uiManager.hideLoadingOverlay();
      uiManager.showNotification('Failed to connect to weather API. Please ensure the backend server is running.', 'error');
      uiManager.updateAPIStatus('disconnected', 'Disconnected');
    }
  }

  async checkAPIConnection() {
    try {
      uiManager.updateAPIStatus('connecting', 'Connecting...');
      
      const healthData = await weatherAPI.checkHealth();
      
      console.log('🌐 API Health Check:', healthData);
      uiManager.updateAPIStatus('connected', 'Connected');
      
      return true;
    } catch (error) {
      console.error('🔌 API Connection failed:', error);
      uiManager.updateAPIStatus('disconnected', 'Disconnected');
      throw error;
    }
  }

  setupElectronHandlers() {
    // Check if we're running in Electron
    if (typeof require !== 'undefined') {
      try {
        const { ipcRenderer } = require('electron');
        
        // Handle menu events
        ipcRenderer.on('menu-new-analysis', () => {
          this.resetForm();
        });
        
        ipcRenderer.on('menu-about', () => {
          this.showAboutDialog();
        });
        
        console.log('🖥️ Electron handlers setup complete');
      } catch (error) {
        console.log('🌐 Running in browser mode');
      }
    }
  }

  resetForm() {
    // Clear form inputs
    uiManager.locationInput.value = '';
    uiManager.selectedLocation = null;
    uiManager.activitySelect.value = 'general';
    
    // Reset dates to default
    const today = new Date();
    const nextWeek = new Date();
    nextWeek.setDate(today.getDate() + 7);
    
    uiManager.startDateInput.value = uiManager.formatDateForInput(today);
    uiManager.endDateInput.value = uiManager.formatDateForInput(nextWeek);
    
    // Clear results
    this.clearResults();
    
    // Focus location input
    uiManager.locationInput.focus();
    
    uiManager.showNotification('Form reset. Ready for new analysis.', 'info');
  }

  clearResults() {
    // Reset overall risk display
    uiManager.riskScore.textContent = '--';
    uiManager.riskScore.className = 'risk-score';
    uiManager.riskDescription.textContent = 'Select a location and dates to analyze weather risk';
    
    // Clear risk categories
    uiManager.riskCategories.innerHTML = '';
    
    // Reset recommendations
    uiManager.recommendationsList.innerHTML = '<li>Enter your location and travel dates to receive personalized recommendations</li>';
    
    // Hide data years
    uiManager.dataYears.style.display = 'none';
    
    // Clear location display
    uiManager.resultLocation.innerHTML = '';
    
    // Clear charts
    if (window.chartManager) {
      chartManager.clearCharts();
    }
  }

  showAboutDialog() {
    const aboutContent = `
      <div style="text-align: center; padding: var(--spacing-xl);">
        <div style="font-size: 3rem; color: var(--nasa-red); margin-bottom: var(--spacing-md);">
          <i class="fas fa-satellite"></i>
        </div>
        <h2 style="color: var(--nasa-blue); margin-bottom: var(--spacing-md);">
          NASA Weather Risk Detection
        </h2>
        <p style="margin-bottom: var(--spacing-lg); color: var(--text-secondary);">
          Personalized weather risk assessment for outdoor activities using NASA POWER Earth observation data.
        </p>
        <div style="background: var(--surface-hover); padding: var(--spacing-lg); border-radius: var(--radius-lg); margin-bottom: var(--spacing-lg);">
          <h3 style="color: var(--text-primary); margin-bottom: var(--spacing-md);">Features</h3>
          <ul style="text-align: left; color: var(--text-secondary);">
            <li>🛰️ Real NASA POWER satellite data</li>
            <li>📊 5 weather risk categories</li>
            <li>🎯 Activity-specific assessments</li>
            <li>💡 Personalized recommendations</li>
            <li>🌍 Global location coverage</li>
          </ul>
        </div>
        <p style="font-size: 0.875rem; color: var(--text-muted);">
          Built for NASA Space Apps Challenge 2025<br>
          Powered by NASA POWER & OpenStreetMap
        </p>
      </div>
    `;

    // Create modal
    const modal = document.createElement('div');
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1002;
      backdrop-filter: blur(4px);
    `;

    const dialog = document.createElement('div');
    dialog.style.cssText = `
      background: var(--surface);
      border-radius: var(--radius-xl);
      box-shadow: var(--shadow-xl);
      max-width: 500px;
      width: 90%;
      max-height: 80vh;
      overflow-y: auto;
    `;

    dialog.innerHTML = aboutContent;

    modal.appendChild(dialog);
    document.body.appendChild(modal);

    // Close on click outside
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        document.body.removeChild(modal);
      }
    });

    // Close on escape key
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        document.body.removeChild(modal);
        document.removeEventListener('keydown', handleEscape);
      }
    };
    document.addEventListener('keydown', handleEscape);
  }

  // Handle application errors
  handleError(error, context = '') {
    console.error(`❌ Error ${context}:`, error);
    
    let message = 'An unexpected error occurred.';
    
    if (error.message) {
      message = error.message;
    } else if (typeof error === 'string') {
      message = error;
    }
    
    uiManager.showNotification(message, 'error');
  }

  // Periodic API health check
  startHealthCheck() {
    setInterval(async () => {
      try {
        await weatherAPI.checkHealth();
        uiManager.updateAPIStatus('connected', 'Connected');
      } catch (error) {
        uiManager.updateAPIStatus('disconnected', 'Disconnected');
      }
    }, 30000); // Check every 30 seconds
  }
}

// Enhanced UI Manager for result display
const originalDisplayResults = uiManager.displayResults;
uiManager.displayResults = function(results) {
  // Call original method
  originalDisplayResults.call(this, results);
  
  // Store results for chart toggle functionality
  window.lastAnalysisResults = results;
  
  // Don't automatically create charts - user must click to see them
  // Charts will be created when user clicks "Show Data Charts" button
};

// Global error handler
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
  if (window.app) {
    app.handleError(event.error, 'Global');
  }
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  if (window.app) {
    app.handleError(event.reason, 'Promise');
  }
});

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  console.log('🌍 DOM loaded, starting NASA Weather Risk Detection App...');
  window.app = new WeatherRiskApp();
  
  // Start periodic health checks
  setTimeout(() => {
    if (window.app.isInitialized) {
      window.app.startHealthCheck();
    }
  }, 5000);
});

// Handle app focus/blur for Electron
if (typeof require !== 'undefined') {
  window.addEventListener('focus', () => {
    if (window.app && window.app.isInitialized) {
      // Refresh API status when app regains focus
      app.checkAPIConnection().catch(console.error);
    }
  });
}