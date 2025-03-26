class SessionState:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.messages = []
        self.module_messages = []
        self.course_selected = False
        self.selected_course = None
        self.current_module_index = -1  # -1 indicates no module selected
        self.current_module_id = None
        self.course_completed = False