from flask import Flask, request, jsonify, send_file, render_template_string
import datetime
import qrcode
import io
import numpy as np
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# --- Mock Databases (Derived from sources) ---
ATTENDANCE_DB = {} [cite: 2, 4]
STUDENT_NAMES = {
    "S001": "Alice Johnson", "S002": "Bob Smith", "S003": "Charlie Brown",
    "S004": "Diana Prince", "S005": "Ethan Hunt"
} [cite: 3]
SCHEDULE_DB = {
    "S001": [{"class": "Introduction to Python", "time": "9:00 AM"}, {"class": "Data Structures", "time": "11:00 AM"}],
    "S002": [{"class": "Web Development", "time": "10:00 AM"}],
    "S003": [{"class": "Machine Learning", "time": "2:00 PM"}]
} [cite: 2, 3]
TASKS_DB = {
    "S001": ["Read chapter 5 of the Python textbook.", "Complete the data structures assignment."],
    "S002": ["Watch the Flask tutorial video."],
    "S003": ["Review linear algebra concepts."]
} [cite: 3, 5]

# --- HTML/CSS Template ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Veyransh | Academic Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8fafc; font-family: 'Inter', sans-serif; }
        .card { background: white; border-radius: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }
    </style>
</head>
<body class="p-4 md:p-10">
    <div class="max-w-6xl mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-center mb-10 card p-8">
            <div>
                <h1 class="text-4xl font-black text-blue-600">🚀 Veyransh</h1>
                <p class="text-slate-500 font-medium">Smart Study & Attendance Assistant</p>
            </div>
            <div class="mt-4 md:mt-0 text-center md:text-right">
                <p class="text-lg font-bold text-slate-700" id="live-clock"></p>
                <p class="text-sm text-blue-500 font-bold uppercase tracking-widest">System Active</p>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div class="space-y-8">
                <div class="card p-6">
                    <h2 class="text-xl font-bold mb-6 flex items-center"><i class="fa-solid fa-id-card mr-3 text-blue-500"></i> Mark Attendance</h2>
                    <label class="block text-sm font-bold text-slate-500 mb-2">Select Student</label>
                    <select id="student-select" class="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl mb-6 outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                        {% for id, name in students.items() %}
                        <option value="{{ id }}">{{ id }} - {{ name }}</option>
                        {% endfor %}
                    </select>
                    <button onclick="markAttendance()" class="w-full bg-blue-600 text-white font-black py-4 rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-200 active:transform active:scale-95 transition-all">
                        LOG PRESENCE
                    </button>
                </div>

                <div class="card p-6 text-center">
                    <h2 class="text-lg font-bold mb-4 text-slate-700">Digital Identity</h2>
                    <div class="bg-white p-4 inline-block rounded-2xl border-2 border-dashed border-slate-200">
                        <img id="qr-display" src="/generate_qr/S001" class="w-44 h-44">
                    </div>
                    <p class="text-xs text-slate-400 mt-4 font-bold uppercase">Dynamic QR Verification</p>
                </div>
            </div>

            <div class="lg:col-span-2 space-y-8">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div class="card p-6">
                        <h2 class="font-bold text-lg mb-4 flex items-center"><i class="fa-solid fa-calendar-day mr-2 text-orange-500"></i> Today's Classes</h2>
                        <div id="schedule-list" class="space-y-3"></div>
                    </div>
                    <div class="card p-6">
                        <h2 class="font-bold text-lg mb-4 flex items-center"><i class="fa-solid fa-list-check mr-2 text-green-500"></i> Active Tasks</h2>
                        <ul id="tasks-list" class="space-y-3"></ul>
                    </div>
                </div>

                <div class="card p-8">
                    <h2 class="font-bold text-xl mb-6 text-slate-800">Academic Growth Visualization</h2>
                    <div class="overflow-hidden rounded-xl border border-slate-100">
                        <img id="performance-chart" src="/performance_plot/S001" class="w-full h-auto">
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('live-clock').innerText = now.toLocaleTimeString() + ' | ' + now.toLocaleDateString();
        }
        setInterval(updateClock, 1000);
        updateClock();

        const studentSelect = document.getElementById('student-select');
        studentSelect.addEventListener('change', (e) => updateDashboard(e.target.value));

        async function updateDashboard(sid) {
            document.getElementById('qr-display').src = `/generate_qr/${sid}`;
            document.getElementById('performance-chart').src = `/performance_plot/${sid}?t=` + new Date().getTime();

            const res = await fetch(`/get_data/${sid}`);
            const data = await res.json();

            const sList = document.getElementById('schedule-list');
            sList.innerHTML = data.schedule.length ? data.schedule.map(s => `
                <div class="flex justify-between items-center p-4 bg-blue-50 rounded-xl border border-blue-100">
                    <span class="font-bold text-slate-700">${s.class}</span>
                    <span class="text-sm font-black text-blue-600 bg-white px-3 py-1 rounded-full shadow-sm">${s.time}</span>
                </div>
            `).join('') : '<p class="text-slate-400 italic">No classes today</p>';

            const tList = document.getElementById('tasks-list');
            tList.innerHTML = data.tasks.length ? data.tasks.map(t => `
                <li class="flex items-start p-3 bg-slate-50 rounded-xl border border-slate-100">
                    <i class="fa-solid fa-circle-check text-green-500 mt-1 mr-3"></i>
                    <span class="text-sm text-slate-600 font-medium">${t}</span>
                </li>
            `).join('') : '<p class="text-slate-400 italic">All caught up!</p>';
        }

        async function markAttendance() {
            const sid = studentSelect.value;
            const res = await fetch('/attendance', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({student_id: sid})
            });
            const data = await res.json();
            alert("Success: " + data.message);
        }

        updateDashboard('S001');
    </script>
</body>
</html>
"""

# --- Flask Routes ---

@app.route('/')
def index():
    return render_template_string(HTML_UI, students=STUDENT_NAMES)

@app.route('/attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    student_id = data.get('student_id')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if student_id not in ATTENDANCE_DB:
        ATTENDANCE_DB[student_id] = []
    ATTENDANCE_DB[student_id].append(timestamp)
    return jsonify({"message": f"Attendance marked for {STUDENT_NAMES.get(student_id, student_id)}", "time": timestamp})

@app.route('/get_data/<student_id>')
def get_data(student_id):
    return jsonify({
        "schedule": SCHEDULE_DB.get(student_id, []),
        "tasks": TASKS_DB.get(student_id, []),
        "name": STUDENT_NAMES.get(student_id, "Unknown")
    })

@app.route('/generate_qr/<student_id>')
def generate_qr(student_id):
    qr = qrcode.make(student_id)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/performance_plot/<student_id>')
def performance_plot(student_id):
    weeks = list(range(1, 8))
    scores = np.random.randint(65, 98, size=7)
    plt.figure(figsize=(10, 4))
    plt.plot(weeks, scores, marker='o', color='#2563eb', linewidth=3, markersize=8)
    plt.fill_between(weeks, scores, color='#dbeafe', alpha=0.5)
    plt.title(f"Performance Analysis: {student_id}", fontsize=14, fontweight='bold')
    plt.xlabel("Study Weeks", fontweight='bold')
    plt.ylabel("Performance Score %", fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
