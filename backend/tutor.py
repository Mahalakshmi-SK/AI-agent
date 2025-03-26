from config import client
from courses import get_courses, get_modules, get_module_content
from chat_history import save_chat_history
from state import SessionState

class Tutor:
    def __init__(self):
        self.state = SessionState()
    
    def process_user_message(self, user_input):
        if self.state.course_completed:
            return "🎉 Course completed! Start a new session to begin again."
        
        # Add user message to history
        self._add_message("user", user_input)
        
        # Handle special commands
        if user_input.lower() == "/next":
            return self._handle_next_module()
        
        if not self.state.course_selected:
            return self._handle_course_selection(user_input)
        
        return self._handle_regular_message(user_input)

    def _handle_next_module(self):
        if not self.state.course_selected:
            return "❌ Please select a course first."
        
        modules = get_modules(self.state.selected_course)
        if self.state.current_module_index >= len(modules) - 1:
            self.state.course_completed = True
            save_chat_history(self.state)
            return "🎉 Course completed! Final chat history saved."
        
        # Save current module history
        save_chat_history(self.state)
        
        # Move to next module
        self.state.current_module_index += 1
        new_module_id, new_module_name = modules[self.state.current_module_index]
        self.state.current_module_id = new_module_id
        
        # Reset module messages for new module
        self.state.module_messages = []
        
        # Get and return new module content
        content = get_module_content(self.state.selected_course, new_module_id)
        response = f"📘 Module {new_module_id}: {new_module_name}\n{content}"
        self._add_message("assistant", response)
        return response

    def _handle_course_selection(self, user_input):
        courses = get_courses()
        selected_course = next((c for c in courses if c.lower() == user_input.lower()), None)
        
        if not selected_course:
            return f"❌ Available courses: {', '.join(courses)}"
        
        self.state.course_selected = True
        self.state.selected_course = selected_course
        modules = get_modules(selected_course)
        
        if not modules:
            return f"❌ No modules found for {selected_course}"
        
        self.state.current_module_index = 0
        self.state.current_module_id = modules[0][0]
        
        # Start first module
        content = get_module_content(selected_course, modules[0][0])
        response = f"✅ Selected {selected_course}\n📘 Module {modules[0][0]}: {modules[0][1]}\n{content}"
        self._add_message("assistant", response)
        return response

    def _handle_regular_message(self, user_input):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{
                    "role": "system",
                    "content": f"""Teach {self.state.selected_course} Module {self.state.current_module_id}.
                    Content: {get_module_content(self.state.selected_course, self.state.current_module_id)}"""
                }] + self.state.module_messages
            )
            ai_response = response.choices[0].message.content
            self._add_message("assistant", ai_response)
            return ai_response
        except Exception as e:
            error = f"⚠️ Error: {str(e)}"
            self._add_message("assistant", error)
            return error

    def _add_message(self, role, content):
        self.state.messages.append({"role": role, "content": content})
        if role != "system":  # Don't store system messages in module context
            self.state.module_messages.append({"role": role, "content": content})