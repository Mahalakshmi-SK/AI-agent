import os
import json
import re
import groq
import streamlit as st

# Load API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("API key not found! Set the GROQ_API_KEY environment variable.")
    st.stop()

# Initialize Groq API client
client = groq.Client(api_key=GROQ_API_KEY)

# Load course data from JSON file
with open("course_data.json", "r") as f:
    course_data = json.load(f)

# Streamlit UI
st.set_page_config(page_title="AI Quiz Generator", layout="wide")

st.title("🧠 AI-Powered Quiz Generator")
st.write("Select a **course** and **module**, and I'll generate a 5-question quiz for you! 🚀")

QUIZ_FILE = "quiz.json"

# Function to fetch course names from JSON data
def fetch_course_names():
    return list(course_data["Course"].keys())

# Function to fetch module names from JSON data
def fetch_module_names(selected_course):
    modules = []
    for module in course_data["Course"][selected_course]:
        modules.append((module["Module"], module["Name"]))
    return modules

# Fetch course names for selection
courses = fetch_course_names()
course_name = st.selectbox("📚 Select Course", options=courses)

# Fetch module names for selection
modules = fetch_module_names(course_name)
module_options = {module[0]: module[1] for module in modules}

# Module selection
module_id = st.selectbox("📚 Select Module", options=list(module_options.keys()), format_func=lambda x: module_options[x])
module_name = module_options[module_id]

# Function to extract JSON from AI response
def extract_json(response_text):
    """Extracts JSON from AI response text, removing extra text and Markdown formatting."""
    match = re.search(r"\[\s*{.*}\s*\]", response_text, re.DOTALL)  # Extract JSON block
    if match:
        return match.group(0)  # Return only the JSON part
    return None  # No valid JSON found

# Function to generate 5 quiz questions using Groq API and save to JSON file
def generate_quiz(module_name):
    st.info(f"🔍 Generating a 5-question quiz for module: **{module_name}**...")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Use latest Groq model
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI quiz generator. Your task is to generate a **5-question multiple-choice quiz** "
                    "in **valid JSON format**. The JSON should follow this structure:\n\n"
                    '[\n'
                    '  {\n'
                    '    "question": "<quiz question>",\n'
                    '    "options": ["<option 1>", "<option 2>", "<option 3>", "<option 4>"],\n'
                    '    "correct_answer": "<correct option>",\n'
                    '    "explanation": "<brief explanation>"\n'
                    '  },\n'
                    '  { "question": "...", "options": [...], "correct_answer": "...", "explanation": "..." },\n'
                    '  ...\n'
                    ']'
                    "\n\n"
                    "Now, generate **5 JSON-formatted quiz questions** related to: " + module_name
                ),
            }
        ]
    )

    # Debugging: Show AI raw response
    raw_response = response.choices[0].message.content
    st.code(raw_response, language="json")  # Display raw JSON response

    json_text = extract_json(raw_response)  # Extract only the JSON block
    if not json_text:
        st.error("❌ AI response did not contain valid JSON.")
        return None

    try:
        quiz_data = json.loads(json_text)  # Convert JSON string to dictionary (list of questions)
        if not isinstance(quiz_data, list) or len(quiz_data) != 5:
            raise ValueError("Invalid format: Expected a list of 5 questions.")

        with open(QUIZ_FILE, "w") as f:
            json.dump(quiz_data, f, indent=4)  # Save JSON file

        return quiz_data
    except (json.JSONDecodeError, ValueError) as e:
        st.error(f"❌ Failed to parse AI-generated JSON: {str(e)}")
        return None

# Function to load quiz from JSON file
def load_quiz():
    if os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE, "r") as f:
            return json.load(f)
    return None

# Generate quiz when the button is clicked
if st.button("🎯 Generate Quiz"):
    quiz_data = generate_quiz(module_name)
    if quiz_data:
        st.success("✅ Quiz Generated! Answer the questions below.")
    else:
        st.error("❌ Failed to generate a valid quiz. Try again.")

# Load and display quiz from JSON
quiz_data = load_quiz()
if quiz_data:
    st.subheader("📢 Quiz Questions:")
    user_answers = {}

    for i, question_data in enumerate(quiz_data):
        st.markdown(f"### **Q{i+1}: {question_data['question']}**")

        # Display options as radio buttons
        user_answers[i] = st.radio(f"Choose the correct answer for Q{i+1}:", question_data["options"], key=f"quiz_q{i}")

    if st.button("✅ Submit Answers"):
        correct_count = 0
        for i, question_data in enumerate(quiz_data):
            if user_answers[i] == question_data["correct_answer"]:
                st.success(f"✅ Q{i+1}: Correct!")
                correct_count += 1
            else:
                st.error(f"❌ Q{i+1}: Incorrect! Correct answer: **{question_data['correct_answer']}**")

            # Show explanation
            st.info(f"📖 Explanation: {question_data['explanation']}")

        st.subheader(f"🎯 Your Score: {correct_count}/5")
