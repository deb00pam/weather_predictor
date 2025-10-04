import google.generativeai as genai
from config import Config

# Configure API
genai.configure(api_key=Config.GEMINI_API_KEY)

print("🔍 Available Gemini models:")
try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")

# Test with different model names
models_to_test = [
    'gemini-1.5-pro',
    'gemini-1.5-flash',
    'gemini-pro',
    'models/gemini-1.5-pro',
    'models/gemini-1.5-flash',
    'models/gemini-pro'
]

print("\n🧪 Testing models:")
for model_name in models_to_test:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, just testing!")
        print(f"✅ {model_name} - WORKS")
        break
    except Exception as e:
        print(f"❌ {model_name} - {str(e)[:100]}...")