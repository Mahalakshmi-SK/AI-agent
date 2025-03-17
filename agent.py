import os
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

# Function to fetch course content from database
def fetch_course_content(module_id):
    db_cursor.execute("SELECT content FROM CourseModules WHERE module_id = ?", (module_id,))
    result = db_cursor.fetchone()
    return result[0] if result else "Content not found."

# Function to fetch module names from database
def fetch_module_names():
    db_cursor.execute("SELECT Module, Name FROM CourseModules")
    return db_cursor.fetchall()

# Fetch module names for selection
modules = fetch_module_names()
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
for message in st.session_state.conversation_memory:
    if message["role"] == "user":
        st.text_area("👤 You:", value=message["content"], height=70, disabled=True)
    elif message["role"] == "assistant":
        st.text_area("🤖 AI Tutor:", value=message["content"], height=150, disabled=True)  # Increased height for detailed responses

if st.button("Finish Module"):
    st.success("Module finished! Proceed to the quiz.")
    # Redirect to quiz page (handled in gui.py)
