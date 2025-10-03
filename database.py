"""
Database setup for WeatherWise
Handles ML model storage, user data, and weather predictions
"""

import sqlite3
import pickle
import json
from datetime import datetime
from typing import Dict, Any, Optional
import os

class WeatherDatabase:
    def __init__(self, db_path: str = "weatherwise.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ML Models table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT UNIQUE NOT NULL,
                model_type TEXT NOT NULL,
                model_data BLOB NOT NULL,
                metadata TEXT,
                accuracy REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Model scalers table (for preprocessing)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_scalers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scaler_name TEXT UNIQUE NOT NULL,
                scaler_data BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Weather predictions cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                activity TEXT NOT NULL,
                prediction_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User queries log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                query_data TEXT NOT NULL,
                response_data TEXT,
                response_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Model performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                test_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # App configuration
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database initialized: {self.db_path}")
    
    def save_model(self, model_name: str, model_obj: Any, model_type: str = "sklearn", 
                   metadata: Dict = None, accuracy: float = None):
        """Save ML model to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Serialize model
        model_data = pickle.dumps(model_obj)
        metadata_json = json.dumps(metadata) if metadata else None
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO ml_models 
                (model_name, model_type, model_data, metadata, accuracy, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (model_name, model_type, model_data, metadata_json, accuracy, datetime.now()))
            
            conn.commit()
            print(f"Model '{model_name}' saved to database")
            
        except Exception as e:
            print(f"Error saving model {model_name}: {e}")
        finally:
            conn.close()
    
    def load_model(self, model_name: str):
        """Load ML model from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT model_data, model_type, metadata, accuracy 
                FROM ml_models WHERE model_name = ?
            ''', (model_name,))
            
            result = cursor.fetchone()
            if result:
                model_data, model_type, metadata, accuracy = result
                model_obj = pickle.loads(model_data)
                
                metadata_dict = json.loads(metadata) if metadata else {}
                return {
                    'model': model_obj,
                    'type': model_type,
                    'metadata': metadata_dict,
                    'accuracy': accuracy
                }
            else:
                print(f"Model '{model_name}' not found in database")
                return None
                
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            return None
        finally:
            conn.close()
    
    def save_scaler(self, scaler_name: str, scaler_obj: Any):
        """Save data scaler to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        scaler_data = pickle.dumps(scaler_obj)
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO model_scalers (scaler_name, scaler_data)
                VALUES (?, ?)
            ''', (scaler_name, scaler_data))
            
            conn.commit()
            print(f"Scaler '{scaler_name}' saved to database")
            
        except Exception as e:
            print(f"Error saving scaler {scaler_name}: {e}")
        finally:
            conn.close()
    
    def load_scaler(self, scaler_name: str):
        """Load data scaler from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT scaler_data FROM model_scalers WHERE scaler_name = ?', 
                          (scaler_name,))
            
            result = cursor.fetchone()
            if result:
                scaler_data = result[0]
                return pickle.loads(scaler_data)
            else:
                print(f"Scaler '{scaler_name}' not found in database")
                return None
                
        except Exception as e:
            print(f"Error loading scaler {scaler_name}: {e}")
            return None
        finally:
            conn.close()
    
    def cache_prediction(self, date: str, latitude: float, longitude: float, 
                        activity: str, prediction_data: Dict):
        """Cache weather prediction for faster future queries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO weather_predictions 
                (date, latitude, longitude, activity, prediction_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, latitude, longitude, activity, json.dumps(prediction_data)))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error caching prediction: {e}")
        finally:
            conn.close()
    
    def get_cached_prediction(self, date: str, latitude: float, longitude: float, 
                             activity: str, tolerance: float = 0.1):
        """Get cached prediction for similar location/date/activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT prediction_data FROM weather_predictions 
                WHERE date = ? AND activity = ? 
                AND ABS(latitude - ?) <= ? AND ABS(longitude - ?) <= ?
                ORDER BY created_at DESC LIMIT 1
            ''', (date, activity, latitude, tolerance, longitude, tolerance))
            
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
            
        except Exception as e:
            print(f"Error getting cached prediction: {e}")
            return None
        finally:
            conn.close()
    
    def log_user_query(self, session_id: str, query_data: Dict, 
                      response_data: Dict = None, response_time: float = None):
        """Log user queries for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_queries 
                (session_id, query_data, response_data, response_time)
                VALUES (?, ?, ?, ?)
            ''', (session_id, json.dumps(query_data), 
                  json.dumps(response_data) if response_data else None, 
                  response_time))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error logging query: {e}")
        finally:
            conn.close()
    
    def save_model_metrics(self, model_name: str, metrics: Dict, test_date: str = None):
        """Save model performance metrics"""
        if not test_date:
            test_date = datetime.now().strftime("%Y-%m-%d")
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for metric_name, metric_value in metrics.items():
                cursor.execute('''
                    INSERT INTO model_metrics 
                    (model_name, metric_name, metric_value, test_date)
                    VALUES (?, ?, ?, ?)
                ''', (model_name, metric_name, float(metric_value), test_date))
            
            conn.commit()
            print(f"Metrics saved for model '{model_name}'")
            
        except Exception as e:
            print(f"Error saving metrics: {e}")
        finally:
            conn.close()
    
    def get_model_info(self):
        """Get information about all stored models"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT model_name, model_type, accuracy, created_at, updated_at
                FROM ml_models ORDER BY updated_at DESC
            ''')
            
            models = []
            for row in cursor.fetchall():
                models.append({
                    'name': row[0],
                    'type': row[1],
                    'accuracy': row[2],
                    'created_at': row[3],
                    'updated_at': row[4]
                })
            
            return models
            
        except Exception as e:
            print(f"Error getting model info: {e}")
            return []
        finally:
            conn.close()
    
    def get_app_config(self, config_key: str, default_value: str = None):
        """Get application configuration value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT config_value FROM app_config WHERE config_key = ?', 
                          (config_key,))
            result = cursor.fetchone()
            return result[0] if result else default_value
            
        except Exception as e:
            print(f"Error getting config {config_key}: {e}")
            return default_value
        finally:
            conn.close()
    
    def set_app_config(self, config_key: str, config_value: str, description: str = None):
        """Set application configuration value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO app_config 
                (config_key, config_value, description, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (config_key, config_value, description, datetime.now()))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error setting config {config_key}: {e}")
        finally:
            conn.close()
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old cached predictions and logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cutoff_date = datetime.now().replace(day=datetime.now().day - days)
            
            cursor.execute('''
                DELETE FROM weather_predictions 
                WHERE created_at < ?
            ''', (cutoff_date,))
            
            cursor.execute('''
                DELETE FROM user_queries 
                WHERE created_at < ?
            ''', (cutoff_date,))
            
            conn.commit()
            print(f"Cleaned up data older than {days} days")
            
        except Exception as e:
            print(f"Error cleaning up data: {e}")
        finally:
            conn.close()
    
    def get_database_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        try:
            # Count records in each table
            tables = ['ml_models', 'model_scalers', 'weather_predictions', 'user_queries', 'model_metrics']
            
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                stats[table] = count
            
            # Database file size
            if os.path.exists(self.db_path):
                stats['db_size_mb'] = round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}
        finally:
            conn.close()

# Database instance
db = WeatherDatabase()

def migrate_pickle_models_to_db():
    """Migrate existing pickle models to database"""
    models_dir = "models"
    if not os.path.exists(models_dir):
        print("No models directory found to migrate")
        return
    
    print("Migrating pickle models to database...")
    
    # Import joblib for loading existing models
    try:
        import joblib
        
        # Migrate scaler
        scaler_path = os.path.join(models_dir, "scaler.pkl")
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
            db.save_scaler("main_scaler", scaler)
        
        # Migrate weather condition models
        conditions = ['very_hot', 'very_cold', 'very_wet', 'very_windy', 'very_uncomfortable']
        for condition in conditions:
            model_path = os.path.join(models_dir, f"{condition}_model.pkl")
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                db.save_model(
                    model_name=condition,
                    model_obj=model,
                    model_type="RandomForestClassifier",
                    metadata={"condition": condition, "migrated_from_pickle": True}
                )
        
        print("Migration completed successfully!")
        print("You can now delete the models/ directory")
        
    except ImportError:
        print("joblib not available for migration")
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    # Initialize database and show stats
    print("WeatherWise Database Setup")
    print("=" * 30)
    
    stats = db.get_database_stats()
    print("Database Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Migrate existing models if they exist
    migrate_pickle_models_to_db()
    
    # Show model info
    models = db.get_model_info()
    if models:
        print("\nStored Models:")
        for model in models:
            print(f"  {model['name']}: {model['type']} (accuracy: {model['accuracy']})")
    else:
        print("\nNo models stored yet")