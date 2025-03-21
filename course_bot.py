import json

try:
    # Load course data from JSON file
    with open('course_data.json', 'r') as file:
        course_data = json.load(file)
except FileNotFoundError:
    print("Error: The course data file was not found.")
    exit()
except json.JSONDecodeError:
    print("Error: The course data file is not a valid JSON.")
    exit()

def chatbot():
    print("Welcome to the Course Chatbot!")
    print("Available courses:", list(course_data["Course"].keys()))
    
    while True:
        course_name = input("Please enter the course you want to learn: ").strip().title()
        
        if course_name in course_data["Course"]:
            print(f"Modules in {course_name} course:")
            for module in course_data["Course"][course_name]:
                print(f"Module {module['Module']}: {module['Name']}")
            break
        else:
            print("Sorry, the course you entered is not available. Please try again.")

if __name__ == "__main__":
    chatbot()
