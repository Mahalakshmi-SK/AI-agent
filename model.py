import groq
import os

# Load API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("API key not found! Set the GROQ_API_KEY environment variable.")

# Initialize client
client = groq.Client(api_key=GROQ_API_KEY)

try:
    # Fetch available models
    models_response = client.models.list()
    
    # Print the models
    print("Available models in your Groq account:")
    for model in models_response.data:
        print(f"- {model['id']}: {model.get('name', 'No name available')}")
except groq.AuthenticationError:
    print("Invalid API Key! Please check your API key.")
except Exception as e:
    print(f"Error fetching models: {e}")
