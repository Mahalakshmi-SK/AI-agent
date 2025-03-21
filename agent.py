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

# Streamlit UI configuration
st.set_page_config(page_title="AI Tutor Chatbot", layout="wide")
st.title("🤖 AI Tutor Chatbot")

# Custom CSS for chat bubbles
st.markdown("""
<style>
    /* User message styling */
    [data-testid="stChatMessage"] > div:has(div.user-message) {
        justify-content: flex-end;
    }
    .user-message {
        background-color: #DCF8C6;
        border-radius: 15px;
        padding: 10px;
        margin: 5px;
        max-width: 70%;
    }
    
    /* AI message styling */
    [data-testid="stChatMessage"] > div:has(div.ai-message) {
        justify-content: flex-start;
    }
    .ai-message {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 10px;
        margin: 5px;
        max-width: 70%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "📚 Enter Course Name"}
    ]

if "course_selected" not in st.session_state:
    st.session_state.course_selected = False

if "current_module_index" not in st.session_state:
    st.session_state.current_module_index = 0

# Helper functions
def get_courses():
    return list(course_data["Course"].keys())

def get_modules(course_name):
    return [(m["Module"], m["Name"]) for m in course_data["Course"][course_name]]

def get_module_content(course_name, module_id):
    for m in course_data["Course"][course_name]:
        if m["Module"] == module_id:
            return m["Content"]
    return ""

def save_chat_history():
    if st.session_state.course_selected:
        chat_dir = "chat_history"
        os.makedirs(chat_dir, exist_ok=True)
        filename = f"{st.session_state.selected_course}_{st.session_state.current_module_id}.json"
        with open(os.path.join(chat_dir, filename), "w") as f:
            json.dump(st.session_state.messages, f)

# Chat display
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(f'<div class="ai-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        with st.chat_message("user"):
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)

# Chat input and processing
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    if not st.session_state.course_selected:
        # Course selection phase
        courses = get_courses()
        if user_input.title() in courses:
            st.session_state.course_selected = True
            st.session_state.selected_course = user_input.title()
            modules = get_modules(st.session_state.selected_course)
            st.session_state.current_module_index = 0
            current_module_id, current_module_name = modules[st.session_state.current_module_index]
            st.session_state.current_module_id = current_module_id
            
            # Add assistant response
            content = get_module_content(st.session_state.selected_course, current_module_id)
            response = f"""✅ Course selected: **{st.session_state.selected_course}**
            
**Starting Module {current_module_id}: {current_module_name}**
{content}
            
What would you like to learn first?"""
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            response = f"""❌ Course not available. Please choose from:
{chr(10).join(['- ' + c for c in courses])}"""
            st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    else:
        # Normal chat processing
        current_course = st.session_state.selected_course
        current_module_id = st.session_state.current_module_id
        module_content = get_module_content(current_course, current_module_id)
        
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"""
                    You are a {current_course} tutor teaching module {current_module_id}. 
                    Module content: {module_content}
                    Respond with detailed explanations, examples, and analogies.
                    """},
                    *st.session_state.messages
                ]
            )
            ai_response = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Error: {str(e)}"})
        st.rerun()

# Module navigation controls
if st.session_state.course_selected:
    modules = get_modules(st.session_state.selected_course)
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.session_state.current_module_index < len(modules) - 1:
            if st.button("Next Module ➡️"):
                save_chat_history()
                st.session_state.current_module_index += 1
                new_module_id, new_module_name = modules[st.session_state.current_module_index]
                st.session_state.current_module_id = new_module_id
                content = get_module_content(st.session_state.selected_course, new_module_id)
                response = f"""📘 Module {new_module_id}: **{new_module_name}**
{content}
                
What would you like to learn about this topic?"""
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        else:
            st.success("🎉 All modules completed!")

    with col2:
        current_module = modules[st.session_state.current_module_index][1]
        st.write(f"**Current Module:** {current_module}")