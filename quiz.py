import os
import json
import groq
import streamlit as st
import sqlite3

# Load API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("API key not found! Set the GROQ_API_KEY environment variable.")
    st.stop()

# Initialize Groq API client
client = groq.Client(api_key=GROQ_API_KEY)

# Connect to SQLite database
db_connection = sqlite3.connect("data.db")
db_cursor = db_connection.cursor()

# Streamlit UI
st.set_page_config(page_title="AI Quiz Generator", layout="wide")

st.title("🧠 AI-Powered Quiz Generator")
st.write("Select a **module**, and I'll generate a quiz question for you! 🚀")

QUIZ_FILE = "quiz.json"

# Function to fetch module names from database
def fetch_module_names():
    db_cursor.execute("SELECT Module, Name FROM CourseModules")
    return db_cursor.fetchall()

# Fetch module names for selection
modules = fetch_module_names()
module_options = {module[0]: module[1] for module in modules}

# Module selection
module_id = st.selectbox("📚 Select Module", options=list(module_options.keys()), format_func=lambda x: module_options[x])
module_name = module_options[module_id]

# Function to generate quiz question using Groq API and save to JSON file
def generate_quiz(module_name):
    st.info(f"🔍 Generating quiz for module: **{module_name}**...")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Use the latest Groq model
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI quiz generator. Your task is to generate a multiple-choice quiz question "
                    "in **valid JSON format**. Make sure to return only the JSON object, without extra text. "
                    "The JSON should have this structure:\n\n"
                    "{\n"
                    '  "question": "<quiz question>",\n'
                    '  "options": ["<option 1>", "<option 2>", "<option 3>", "<option 4>"],\n'
                    '  "correct_answer": "<correct option>",\n'
                    '  "explanation": "<brief explanation>"\n'
                    "}\n\n"
                    "Now, generate a JSON-formatted quiz question related to: " + module_name
                ),
            }
        ]
    )

    # Debugging: Show AI raw response
    raw_response = response.choices[0].message.content
    st.code(raw_response, language="json")  # Display the raw response for debugging

    try:
        quiz_data = json.loads(raw_response)  # Convert JSON string to dictionary
        with open(QUIZ_FILE, "w") as f:
            json.dump(quiz_data, f, indent=4)  # Save JSON file
        return quiz_data
    except json.JSONDecodeError:
        st.error("❌ AI response is not valid JSON. Please try again.")
        return None

# Function to load quiz from JSON file
def load_quiz():
    if os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE, "r") as f:
            return json.load(f)
    return None

# Generate quiz when the button is clicked
if st.button("🎯 Generate Quiz Question"):
    quiz_data = generate_quiz(module_name)
    if quiz_data:
        st.success("✅ Quiz Generated! Answer the question below.")
    else:
        st.error("❌ Failed to generate a valid quiz. Try again.")

# Load and display quiz from JSON
quiz_data = load_quiz()
if quiz_data:
    st.subheader("📢 Quiz Question:")
    st.markdown(f"**{quiz_data['question']}**")

    # Display options as radio buttons
    user_answer = st.radio("Choose the correct answer:", quiz_data["options"], key="quiz_answer")

    if st.button("✅ Submit Answer"):
        if user_answer == quiz_data["correct_answer"]:
            st.success("🎉 Correct! Well done.")
        else:
            st.error(f"❌ Incorrect. The correct answer is: **{quiz_data['correct_answer']}**")

        # Show explanation
        st.info(f"📖 Explanation: {quiz_data['explanation']}")

# Close database connection
db_connection.close()
