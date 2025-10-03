"""
Database Setup Script for WeatherWise
Run this after cloning the repository to set up the database
"""

import os
import sys
from database import WeatherDatabase
from weather_processor import WeatherProcessor

def setup_database():
    """Initialize database and train models for new installations"""
    print("🏗️  WeatherWise Database Setup")
    print("=" * 40)
    
    # Check if database already exists
    if os.path.exists("weatherwise.db"):
        print("⚠️  Database already exists!")
        response = input("Do you want to recreate it? (y/N): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            return
        else:
            os.remove("weatherwise.db")
            print("🗑️  Removed existing database")
    
    # Initialize database
    print("\n1️⃣  Initializing database...")
    db = WeatherDatabase()
    print("✅ Database initialized")
    
    # Check for weather data
    if not os.path.exists("data/weather.csv"):
        print("\n❌ Error: data/weather.csv not found!")
        print("Please ensure the weather data file is in the project directory.")
        sys.exit(1)
    
    # Train models
    print("\n2️⃣  Training machine learning models...")
    print("This may take a few minutes...")
    
    try:
        processor = WeatherProcessor()
        
        # Load and process data
        df = processor.load_and_preprocess_data()
        features = processor.create_features(df)
        classifications = processor.create_weather_classifications(df)
        
        # Train models
        results = processor.train_models(features, classifications)
        
        print("✅ Models trained and saved to database")
        
        # Show results summarygit 
        print("\n📊 Training Results:")
        for condition, metrics in results.items():
            accuracy = metrics.get('test_accuracy', 0)
            examples = metrics.get('positive_examples', 0)
            print(f"   {condition.replace('_', ' ').title()}: {accuracy:.3f} accuracy ({examples} examples)")
        
    except Exception as e:
        print(f"\n❌ Error during model training: {e}")
        sys.exit(1)
    
    # Verify setup
    print("\n3️⃣  Verifying setup...")
    
    # Check database contents
    stats = db.get_database_stats()
    models = db.get_model_info()
    
    print(f"   Models stored: {len(models)}")
    print(f"   Database size: {stats.get('db_size_mb', 0):.1f} MB")
    
    if len(models) >= 5:  # Should have 5 weather condition models
        print("✅ Setup completed successfully!")
        
        print("\n🚀 Next Steps:")
        print("   1. Start the API server: python api_server.py")
        print("   2. Open http://localhost:8000/docs in your browser")
        print("   3. Test the API endpoints")
        
    else:
        print("⚠️  Setup completed but some models may be missing")

def main():
    """Main setup function"""
    print("Welcome to WeatherWise setup!")
    print("This script will initialize the database and train ML models.")
    print("Required: data/weather.csv file must be present in the data directory.")
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Check dependencies
    try:
        import pandas
        import sklearn
        import fastapi
        print("✅ Dependencies verified")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Run setup
    setup_database()

if __name__ == "__main__":
    main()