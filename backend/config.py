# config.py
import os
import groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("API key not found! Set the GROQ_API_KEY environment variable.")
    exit()

client = groq.Client(api_key=GROQ_API_KEY)
