from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# Mock Databases (simulating a real database)
ATTENDANCE_DB = {}
SCHEDULE_DB = {
    "S001": [
        {"class": "Introduction to Python", "time": "9:00 AM"},
        {"class": "Data Structures", "time": "11:00 AM"}
    ],
    "S002": [
        {"class": "Web Development", "time": "10:00 AM"},
        {"class": "Introduction to Python", "time": "1:00 PM"}
    ],
    "S003": [
        {"class": "Machine Learning", "time": "2:00 PM"}
    ]
}
TASKS_DB = {
    "S001": ["Read chapter 5 of the Python textbook.", "Complete the data structures assignment."],
    "S002": ["Watch the Flask tutorial video.", "Start the project for Web Development."],
    "S003": ["Review linear algebra concepts.", "Set up the environment for your ML model."]
}
GOALS_DB = {
    "S001": ["Learn Git", "Improve public speaking"],
    "S002": ["Build a personal portfolio website"],
    "S003": ["Contribute to an open-source project"]
}

# A simple route to confirm the server is running.
@app.route('/')
def hello():
    return "The Flask backend is running!"

@app.route('/update_data', methods=['POST'])
def update_data():
    data = request.json
    global SCHEDULE_DB, TASKS_DB, GOALS_DB
    
    new_students = data.get('students', {})
    for student_id in new_students.keys():
        if student_id not in SCHEDULE_DB:
            SCHEDULE_DB[student_id] = [{"class": "New Student Orientation", "time": "10:00 AM"}]
            TASKS_DB[student_id] = ["Explore the campus map."]
            GOALS_DB[student_id] = ["Get comfortable with the new environment."]
            
    return jsonify({"message": "Data updated successfully on the backend."})

@app.route('/attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    student_id = data.get('student_id')
    class_id = data.get('class_id')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if student_id not in ATTENDANCE_DB:
        ATTENDANCE_DB[student_id] = {}
    
    if class_id not in ATTENDANCE_DB[student_id]:
        ATTENDANCE_DB[student_id][class_id] = []

    ATTENDANCE_DB[student_id][class_id].append(timestamp)
    return jsonify({"message": f"Attendance marked for Student {student_id} in Class {class_id} at {timestamp}"})

@app.route('/realtime_attendance/<class_id>', methods=['GET'])
def get_realtime_attendance(class_id):
    realtime_data = {}
    for student_id, classes in ATTENDANCE_DB.items():
        if class_id in classes:
            realtime_data[student_id] = "Present"
    return jsonify(realtime_data)

@app.route('/schedule/<student_id>', methods=['GET'])
def get_schedule(student_id):
    schedule = SCHEDULE_DB.get(student_id)
    if schedule:
        return jsonify(schedule)
    return jsonify({"error": "Student schedule not found."}), 404

@app.route('/tasks/<student_id>', methods=['GET'])
def get_tasks(student_id):
    tasks = TASKS_DB.get(student_id, [])
    if tasks:
        return jsonify(tasks)
    return jsonify({"message": "No personalized tasks found for this student."}), 404

@app.route('/daily_routine/<student_id>', methods=['GET'])
def get_daily_routine(student_id):
    schedule = SCHEDULE_DB.get(student_id, [])
    tasks = TASKS_DB.get(student_id, [])
    goals = GOALS_DB.get(student_id, [])
    
    routine = []
    
    for item in schedule:
        routine.append({"time": item["time"], "activity": f"Class: {item['class']}"})
        
    routine.append({"time": "12:00 PM", "activity": "Study for upcoming tests."})
    
    if tasks:
        routine.append({"time": "4:00 PM", "activity": f"Work on a personalized task: {tasks[0]}"})
    
    if goals:
        routine.append({"time": "6:00 PM", "activity": f"Work towards a long-term goal: {goals[0]}"})
        
    routine.sort(key=lambda x: datetime.datetime.strptime(x['time'], "%I:%M %p"))
    
    return jsonify(routine)

if __name__ == '__main__':
    app.run(debug=True)
