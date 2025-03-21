import os
import groq
import streamlit as st
import json

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
st.set_page_config(page_title="AI Tutor Chatbot", layout="wide")

st.title("🤖 AI Tutor Chatbot")
st.write("Ask me anything, and I'll guide you with **detailed explanations!** 🚀")

# Store conversation in session state
if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = [
        {
            "role": "system", 
            "content": (
                "You are an AI tutor specialized in explaining concepts in detail. "
                "Whenever a user asks a question, provide a **clear, step-by-step explanation** with **examples, analogies, and code snippets** (if applicable). "
                "Your goal is to ensure the user fully understands the concept, even if they are a beginner."
            )
        }
    ]

# Function to get AI response
def get_response(user_input, module_name):
    st.session_state.conversation_memory.append({"role": "user", "content": f"{user_input} (Module: {module_name})"})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Use an available Groq model
        messages=st.session_state.conversation_memory
    )

    ai_response = response.choices[0].message.content
    st.session_state.conversation_memory.append({"role": "assistant", "content": ai_response})

    return ai_response

# Function to fetch course content from JSON data
def fetch_course_content(module_id, selected_course):
    for module in course_data["Course"][selected_course]:
        if module["Module"] == module_id:
            return module["Content"]
    return "Content not found."

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

# Module selection and completion
module_id = st.selectbox("Select Module", options=list(module_options.keys()), format_func=lambda x: module_options[x])
module_name = module_options[module_id]

# Chat input box
user_input = st.text_input("Type your question and press Enter:", key="user_input")

if user_input:
    response = get_response(user_input, module_name)
    st.markdown(f"**🤖 AI Tutor:** {response}")

# Display chat history
st.subheader("📜 Chat History")
for i, message in enumerate(st.session_state.conversation_memory):
    if message["role"] == "user":
        st.text_area("👤 You:", value=message["content"], height=70, disabled=True, key=f"user_{i}")
    elif message["role"] == "assistant":
        st.text_area("🤖 AI Tutor:", value=message["content"], height=150, disabled=True, key=f"assistant_{i}")  # Increased height for detailed responses
