// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize)]
struct WeatherPrediction {
    very_hot: f64,
    very_cold: f64,
    very_windy: f64,
    very_wet: f64,
    very_uncomfortable: f64,
}

#[derive(Debug, Serialize, Deserialize)]
struct PredictionRequest {
    temperature: f64,
    humidity: f64,
    wind_speed: f64,
    pressure: f64,
    activity: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct ApiResponse {
    prediction: WeatherPrediction,
    activity_risk: String,
    recommendation: String,
    timestamp: String,
}

// Tauri command to get weather prediction from Python backend
#[tauri::command]
async fn get_weather_prediction(
    temperature: f64,
    humidity: f64,
    wind_speed: f64,
    pressure: f64,
    activity: String,
) -> Result<ApiResponse, String> {
    let client = reqwest::Client::new();
    
    let request_data = PredictionRequest {
        temperature,
        humidity,
        wind_speed,
        pressure,
        activity,
    };

    let response = client
        .post("http://localhost:8000/predict")
        .json(&request_data)
        .send()
        .await
        .map_err(|e| format!("Failed to send request: {}", e))?;

    if response.status().is_success() {
        let api_response: ApiResponse = response
            .json()
            .await
            .map_err(|e| format!("Failed to parse response: {}", e))?;
        
        Ok(api_response)
    } else {
        Err(format!("API request failed with status: {}", response.status()))
    }
}

// Tauri command to check backend health
#[tauri::command]
async fn check_backend_health() -> Result<String, String> {
    let client = reqwest::Client::new();
    
    match client.get("http://localhost:8000/health").send().await {
        Ok(response) => {
            if response.status().is_success() {
                Ok("Backend is running".to_string())
            } else {
                Err(format!("Backend returned status: {}", response.status()))
            }
        },
        Err(e) => Err(format!("Cannot connect to backend: {}", e))
    }
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_weather_prediction,
            check_backend_health
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}