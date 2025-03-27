# courses.py
import json
import os

def load_course_data():
    file_path = os.path.join(os.path.dirname(__file__), "course_data.json")
    with open(file_path, "r") as f:
        return json.load(f)

course_data = load_course_data()

def get_courses():
    """Returns a list of available courses."""
    return list(course_data.get("Course", {}).keys())

def get_modules(course_name):
    """Returns a list of modules (ID, Name) for a given course."""
    modules = course_data.get("Course", {}).get(course_name, [])
    if not modules:
        return []
    return [(m.get("Module"), m.get("Name")) for m in modules]

def get_module_content(course_name, module_id):
    """Returns the content of a specific module."""
    modules = course_data.get("Course", {}).get(course_name, [])
    for m in modules:
        if m.get("Module") == module_id:
            return m.get("Content", "No content available for this module.")
    return "Module not found."
