import os
import json
from datetime import datetime

def save_chat_history(state):
    if not state.course_selected or not state.module_messages:
        return
    
    history_dir = "chat_history"
    os.makedirs(history_dir, exist_ok=True)
    
    filename = f"{state.selected_course}_module_{state.current_module_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    
    with open(os.path.join(history_dir, filename), 'w') as f:
        json.dump({
            "course": state.selected_course,
            "module_id": state.current_module_id,
            "messages": state.module_messages
        }, f, indent=2)