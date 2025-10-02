import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import our database module
from database import WeatherDatabase

class WeatherProcessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.models = {}
        self.db = WeatherDatabase()  # Initialize database connection
        self.thresholds = {
            'very_hot': 28,      # Celsius - adjusted to be more realistic
            'very_cold': 10,     # Celsius - adjusted to get some positive examples
            'very_wet': 10,      # mm rainfall
            'very_windy': 25,    # km/h (we'll simulate this for now)
            'very_uncomfortable': None  # Will be calculated based on heat index
        }
        
    def load_and_preprocess_data(self, csv_path='weather.csv'):
        """Load and preprocess weather data"""
        print("Loading weather data...")
        df = pd.read_csv(csv_path)
        
        # Clean column names and data
        if '_id' in df.columns:
            df.drop('_id', axis=1, inplace=True)
        
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Handle missing values
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        # Add simulated wind speed (since not in original data)
        np.random.seed(42)
        df['wind_speed'] = np.random.normal(15, 8, len(df))  # Mean 15 km/h, std 8
        df['wind_speed'] = np.clip(df['wind_speed'], 0, 60)  # Realistic range
        
        # Add humidity simulation (for comfort index)
        df['humidity'] = np.random.normal(65, 20, len(df))  # Mean 65%, std 20
        df['humidity'] = np.clip(df['humidity'], 10, 100)
        
        print(f"Loaded {len(df)} weather records")
        return df
    
    def calculate_comfort_index(self, temp, humidity):
        """Calculate heat index/comfort level"""
        # Simplified heat index calculation for pandas Series
        # Create a copy to avoid modifying original
        hi = temp.copy()
        
        # For temperatures >= 27C, apply heat index formula
        mask = temp >= 27
        hi[mask] = temp[mask] + 0.5 * (temp[mask] - 14.5) * (humidity[mask] / 100)
        
        # For cooler temps, use original temperature
        hi[~mask] = temp[~mask]
        
        return hi
    
    def create_weather_classifications(self, df):
        """Create binary classifications for adverse weather conditions"""
        classifications = pd.DataFrame(index=df.index)
        
        # Calculate comfort index
        df['comfort_index'] = self.calculate_comfort_index(df['temp_max'], df['humidity'])
        
        # Create binary classifications
        classifications['very_hot'] = (df['temp_max'] >= self.thresholds['very_hot']).astype(int)
        classifications['very_cold'] = (df['temp_min'] <= self.thresholds['very_cold']).astype(int)
        classifications['very_wet'] = (df['rain'] >= self.thresholds['very_wet']).astype(int)
        classifications['very_windy'] = (df['wind_speed'] >= self.thresholds['very_windy']).astype(int)
        classifications['very_uncomfortable'] = (df['comfort_index'] >= 35).astype(int)  # Heat index > 35°C
        
        print("Weather classifications created:")
        for col in classifications.columns:
            pct = (classifications[col].mean() * 100)
            print(f"  {col}: {pct:.1f}% of days")
        
        return classifications
    
    def create_features(self, df):
        """Create enhanced features for prediction"""
        features = df.copy()
        
        # Rolling averages
        for window in [3, 7, 14]:
            for col in ['temp_max', 'temp_min', 'rain', 'wind_speed', 'humidity']:
                features[f'{col}_rolling_{window}'] = df[col].rolling(window).mean()
        
        # Seasonal features
        features['month'] = features.index.month
        features['day_of_year'] = features.index.dayofyear
        features['season'] = ((features.index.month - 1) // 3) % 4
        
        # Temperature range and trends
        features['temp_range'] = features['temp_max'] - features['temp_min']
        features['temp_avg'] = (features['temp_max'] + features['temp_min']) / 2
        
        # Lag features
        for lag in [1, 2, 3]:
            for col in ['temp_max', 'temp_min', 'rain', 'wind_speed']:
                features[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        # Monthly and seasonal averages
        for col in ['temp_max', 'temp_min', 'rain']:
            monthly_avg = df.groupby(df.index.month)[col].expanding().mean()
            features[f'{col}_monthly_avg'] = monthly_avg.values
        
        # Fill NaN values created by rolling and lag features
        features = features.fillna(method='ffill').fillna(method='bfill')
        
        return features
    
    def train_models(self, features, classifications, test_size=0.2):
        """Train classification models for each weather condition"""
        print("Training weather classification models...")
        
        # Split data
        split_idx = int(len(features) * (1 - test_size))
        X_train = features.iloc[:split_idx]
        X_test = features.iloc[split_idx:]
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        results = {}
        
        for condition in classifications.columns:
            print(f"Training model for {condition}...")
            
            y_train = classifications[condition].iloc[:split_idx]
            y_test = classifications[condition].iloc[split_idx:]
            
            # Use Random Forest for better probability estimates
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            # Get probability predictions - handle single class case
            try:
                y_prob = model.predict_proba(X_test_scaled)
                if y_prob.shape[1] > 1:
                    y_prob = y_prob[:, 1]  # Probability of positive class
                else:
                    y_prob = y_prob[:, 0]  # Only one class available
            except Exception as e:
                print(f"    Warning: Could not get probabilities for {condition}: {e}")
                y_prob = model.predict(X_test_scaled).astype(float)
            
            self.models[condition] = model
            results[condition] = {
                'train_accuracy': train_score,
                'test_accuracy': test_score,
                'avg_probability': y_prob.mean(),
                'positive_examples': y_train.sum()
            }
            
            # Save model to database with metrics
            model_metadata = {
                'condition': condition,
                'training_samples': len(y_train),
                'positive_examples': int(y_train.sum()),
                'features_count': X_train_scaled.shape[1],
                'trained_date': datetime.now().isoformat()
            }
            
            self.db.save_model(
                model_name=condition,
                model_obj=model,
                model_type="RandomForestClassifier",
                metadata=model_metadata,
                accuracy=test_score
            )
            
            # Save metrics separately for tracking
            metrics = {
                'train_accuracy': train_score,
                'test_accuracy': test_score,
                'avg_probability': y_prob.mean(),
                'positive_examples_ratio': y_train.sum() / len(y_train)
            }
            self.db.save_model_metrics(condition, metrics)
            
            print(f"  Train accuracy: {train_score:.3f}")
            print(f"  Test accuracy: {test_score:.3f}")
            print(f"  Positive examples: {results[condition]['positive_examples']}")
        
        # Save scaler to database
        self.db.save_scaler("main_scaler", self.scaler)
        print("Models and scaler saved to database")
        
        return results
    
    def predict_weather_risks(self, date, location_features=None):
        """Predict weather risks for a given date"""
        # For demo, we'll use the last known features
        # In production, this would use real-time data or forecasts
        
        if location_features is None:
            # Use average features as baseline
            location_features = {
                'temp_max': 25, 'temp_min': 15, 'rain': 2,
                'wind_speed': 15, 'humidity': 65, 'month': date.month,
                'day_of_year': date.timetuple().tm_yday, 'season': ((date.month - 1) // 3) % 4,
                'temp_range': 10, 'temp_avg': 20
            }
        
        # Create feature vector (simplified for demo)
        feature_vector = np.array([[
            location_features.get('temp_max', 25),
            location_features.get('temp_min', 15),
            location_features.get('rain', 2),
            location_features.get('wind_speed', 15),
            location_features.get('humidity', 65),
            location_features.get('month', date.month),
            location_features.get('day_of_year', date.timetuple().tm_yday),
            location_features.get('season', ((date.month - 1) // 3) % 4),
            location_features.get('temp_range', 10),
            location_features.get('temp_avg', 20)
        ] + [25, 15, 2, 15, 65] * 6])  # Simplified rolling and lag features
        
        # Pad to match training features (this is simplified - in production would be more robust)
        if feature_vector.shape[1] < 50:  # Assuming ~50 features
            padding = np.zeros((1, 50 - feature_vector.shape[1]))
            feature_vector = np.hstack([feature_vector, padding])
        
        predictions = {}
        for condition, model in self.models.items():
            try:
                # Get probability of adverse condition
                prob_output = model.predict_proba(feature_vector)
                if prob_output.shape[1] > 1:
                    prob = prob_output[0, 1]  # Probability of positive class
                else:
                    prob = prob_output[0, 0]  # Single class case
                    
                predictions[condition] = {
                    'probability': float(prob),
                    'risk_level': self._get_risk_level(prob),
                    'binary_prediction': bool(prob > 0.5)
                }
            except Exception as e:
                print(f"Error predicting {condition}: {e}")
                predictions[condition] = {
                    'probability': 0.5,
                    'risk_level': 'medium',
                    'binary_prediction': False
                }
        
        return predictions
    
    def _get_risk_level(self, probability):
        """Convert probability to risk level"""
        if probability < 0.2:
            return 'low'
        elif probability < 0.5:
            return 'medium'
        elif probability < 0.8:
            return 'high'
        else:
            return 'very_high'
    
    def save_models(self, path='models/'):
        """Save trained models and scaler - DEPRECATED: Now using database"""
        print("Models are now saved to database automatically during training")
        print("This method is deprecated but kept for compatibility")
    
    def load_models(self, path='models/'):
        """Load trained models and scaler from database"""
        print("Loading models from database...")
        
        # Load scaler
        scaler = self.db.load_scaler("main_scaler")
        if scaler:
            self.scaler = scaler
        else:
            print("Warning: No scaler found in database")
        
        # Load weather condition models
        conditions = ['very_hot', 'very_cold', 'very_wet', 'very_windy', 'very_uncomfortable']
        loaded_count = 0
        
        for condition in conditions:
            model_data = self.db.load_model(condition)
            if model_data:
                self.models[condition] = model_data['model']
                loaded_count += 1
                accuracy = model_data['accuracy'] or 0.0
                print(f"  Loaded {condition} model (accuracy: {accuracy:.3f})")
            else:
                print(f"  Warning: {condition} model not found in database")
        
        if loaded_count > 0:
            print(f"Successfully loaded {loaded_count} models from database")
        else:
            print("No models found in database")
        
        return loaded_count > 0

def main():
    """Example usage"""
    processor = WeatherProcessor()
    
    # Load and process data
    df = processor.load_and_preprocess_data()
    features = processor.create_features(df)
    classifications = processor.create_weather_classifications(df)
    
    # Train models
    results = processor.train_models(features, classifications)
    
    # Save models
    processor.save_models()
    
    # Test prediction
    test_date = datetime(2024, 7, 15)  # Summer date
    predictions = processor.predict_weather_risks(test_date)
    
    print(f"\nWeather risk predictions for {test_date.date()}:")
    for condition, pred in predictions.items():
        print(f"  {condition}: {pred['probability']:.2f} ({pred['risk_level']} risk)")

if __name__ == "__main__":
    main()