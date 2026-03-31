from flask import Flask, request, jsonify, send_file, render_template_string
import datetime
import qrcode
import io
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression # [cite: 66]
import os

app = Flask(__name__)

# --- Extended Mock Databases ---
ATTENDANCE_DB = {}
STUDENT_NAMES = {
    "S001": "Alice Johnson", "S002": "Bob Smith", "S003": "Charlie Brown",
    "S004": "Diana Prince", "S005": "Ethan Hunt"
}
SCHEDULE_DB = {
    "S001": [{"class": "Python", "time": "09:00 AM"}, {"class": "Data Structures", "time": "11:00 AM"}],
    "S002": [{"class": "Web Dev", "time": "10:00 AM"}],
    "S003": [{"class": "Machine Learning", "time": "02:00 PM"}]
}
TASKS_DB = {
    "S001": ["Read Ch 5", "DS Assignment"], "S002": ["Watch Flask Video"], "S003": ["Review Linear Algebra"]
}

# --- UI Template with New Features ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Veyransh Pro | Smart Study Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        body { background: #0f172a; font-family: 'Plus Jakarta Sans', sans-serif; color: white; }
        .glass-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); border-radius: 1.5rem; }
        .btn-primary { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); transition: all 0.3s ease; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4); }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
        <div class="flex flex-col md:flex-row justify-between items-center mb-10 glass-card p-6">
            <div class="flex items-center space-x-4">
                <div class="bg-blue-600 p-3 rounded-2xl text-2xl">🚀</div>
                <div>
                    <h1 class="text-2xl font-black tracking-tight">VEYRANSH <span class="text-blue-500">PRO</span></h1>
                    <p class="text-slate-400 text-xs font-bold uppercase tracking-widest">AI Academic Ecosystem</p>
                </div>
            </div>
            <div class="mt-4 md:mt-0 flex items-center space-x-6">
                <div class="text-right">
                    <p id="live-time" class="text-xl font-bold"></p>
                    <p class="text-slate-500 text-xs" id="live-date"></p>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div class="lg:col-span-4 space-y-8">
                <div class="glass-card p-6">
                    <h3 class="text-lg font-bold mb-4 flex items-center"><i class="fa-solid fa-circle-user mr-2 text-blue-400"></i> Student Console</h3>
                    <select id="student-select" class="w-full p-4 bg-slate-800 border border-slate-700 rounded-xl mb-4 outline-none focus:ring-2 focus:ring-blue-500">
                        {% for id, name in students.items() %}
                        <option value="{{ id }}">{{ id }} - {{ name }}</option>
                        {% endfor %}
                    </select>
                    <button onclick="markAttendance()" class="w-full btn-primary py-4 rounded-xl font-black text-sm uppercase tracking-wider">Mark Present</button>
                </div>

                <div class="glass-card p-6 text-center">
                    <h3 class="text-lg font-bold mb-4"><i class="fa-solid fa-stopwatch mr-2 text-orange-400"></i> Focus Timer</h3>
                    <div class="text-4xl font-black mb-4 text-orange-400" id="timer-display">25:00</div>
                    <div class="flex justify-center space-x-3">
                        <button onclick="toggleTimer()" id="timer-btn" class="bg-slate-700 px-6 py-2 rounded-lg font-bold hover:bg-slate-600">Start</button>
                        <button onclick="resetTimer()" class="bg-slate-700 px-6 py-2 rounded-lg font-bold hover:bg-slate-600">Reset</button>
                    </div>
                </div>

                <div class="glass-card p-6 text-center">
                    <img id="qr-display" src="/generate_qr/S001" class="mx-auto w-32 h-32 bg-white p-2 rounded-xl mb-3">
                    <p class="text-xs text-slate-500 font-bold">DIGITAL CAMPUS ID</p>
                </div>
            </div>

            <div class="lg:col-span-8 space-y-8">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="glass-card p-6 border-l-4 border-blue-500">
                        <h3 class="font-bold mb-2">🤖 AI Grade Predictor</h3>
                        <p class="text-xs text-slate-400 mb-4">Based on your study hours & performance [cite: 68]</p>
                        <div class="flex items-center justify-between">
                            <input type="number" id="study-hours" placeholder="Study Hours" class="w-2/3 bg-slate-800 p-2 rounded-lg text-sm border border-slate-700">
                            <button onclick="predictGrade()" class="bg-blue-600 px-4 py-2 rounded-lg text-xs font-bold">Predict</button>
                        </div>
                        <p id="prediction-result" class="mt-3 text-sm font-bold text-green-400"></p>
                    </div>
                    <div class="glass-card p-6 border-l-4 border-purple-500">
                        <h3 class="font-bold mb-2">🔍 Notes OCR Scanner</h3>
                        <p class="text-xs text-slate-400 mb-4">Extract text from your study notes [cite: 56]</p>
                        <button onclick="simulateOCR()" class="w-full bg-purple-600 py-2 rounded-lg text-xs font-bold hover:bg-purple-700 transition">Scan Uploaded Notes</button>
                        <p id="ocr-result" class="mt-3 text-[10px] text-slate-300 italic truncate"></p>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="glass-card p-6">
                        <h3 class="font-bold text-slate-300 mb-4">📅 Schedule</h3>
                        <div id="schedule-list" class="space-y-3"></div>
                    </div>
                    <div class="glass-card p-6">
                        <h3 class="font-bold text-slate-300 mb-4">✅ Tasks</h3>
                        <div id="tasks-list" class="space-y-3"></div>
                    </div>
                </div>

                <div class="glass-card p-6">
                    <h3 class="font-bold mb-4">📊 Growth Analytics </h3>
                    <img id="performance-chart" src="/performance_plot/S001" class="w-full rounded-xl opacity-90">
                </div>
            </div>
        </div>
    </div>

    <script>
        // Clock & Date Logic
        function updateClock() {
            const now = new Date();
            document.getElementById('live-time').innerText = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});
            document.getElementById('live-date').innerText = now.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
        }
        setInterval(updateClock, 1000); updateClock();

        // Pomodoro Timer Logic
        let timerSeconds = 1500;
        let timerRunning = false;
        let interval;

        function toggleTimer() {
            if (timerRunning) {
                clearInterval(interval);
                document.getElementById('timer-btn').innerText = "Start";
            } else {
                interval = setInterval(() => {
                    timerSeconds--;
                    let mins = Math.floor(timerSeconds / 60);
                    let secs = timerSeconds % 60;
                    document.getElementById('timer-display').innerText = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
                    if (timerSeconds <= 0) resetTimer();
                }, 1000);
                document.getElementById('timer-btn').innerText = "Pause";
            }
            timerRunning = !timerRunning;
        }

        function resetTimer() {
            clearInterval(interval);
            timerSeconds = 1500;
            document.getElementById('timer-display').innerText = "25:00";
            document.getElementById('timer-btn').innerText = "Start";
            timerRunning = false;
        }

        // Dashboard Updates
        const studentSelect = document.getElementById('student-select');
        studentSelect.addEventListener('change', (e) => updateDashboard(e.target.value));

        async function updateDashboard(sid) {
            document.getElementById('qr-display').src = `/generate_qr/${sid}`;
            document.getElementById('performance-chart').src = `/performance_plot/${sid}?t=` + new Date().getTime();

            const res = await fetch(`/get_data/${sid}`);
            const data = await res.json();

            const sList = document.getElementById('schedule-list');
            sList.innerHTML = data.schedule.map(s => `
                <div class="flex justify-between bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                    <span class="font-bold text-sm text-blue-300">${s.class}</span>
                    <span class="text-xs text-slate-500">${s.time}</span>
                </div>
            `).join('');

            const tList = document.getElementById('tasks-list');
            tList.innerHTML = data.tasks.map(t => `
                <div class="flex items-center text-xs text-slate-400 bg-slate-800/30 p-2 rounded-lg">
                    <i class="fa-solid fa-check-circle text-green-500 mr-2"></i> ${t}
                </div>
            `).join('');
        }

        async function markAttendance() {
            const sid = studentSelect.value;
            const res = await fetch('/attendance', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({student_id: sid})
            });
            const data = await res.json();
            alert(data.message);
        }

        async function predictGrade() {
            const hours = document.getElementById('study-hours').value;
            if(!hours) return alert("Enter hours first!");
            const res = await fetch(`/predict_grade?hours=${hours}`);
            const data = await res.json();
            document.getElementById('prediction-result').innerText = "Predicted Grade: " + data.grade + "%";
        }

        function simulateOCR() {
            document.getElementById('ocr-result').innerText = "Scanning... Found text: 'The importance of Linear Regression in Data Science...' [cite: 56]";
        }

        updateDashboard('S001');
    </script>
</body>
</html>
"""

# --- Flask Endpoints with AI Logic ---

@app.route('/')
def index():
    return render_template_string(HTML_UI, students=STUDENT_NAMES)

@app.route('/predict_grade')
def predict_grade():
    hours = float(request.args.get('hours', 0))
    # ML Logic: Linear Regression [cite: 66]
    X = np.array([[2], [4], [6], [8], [10]]) # Study Hours
    y = np.array([50, 65, 75, 88, 95])       # Grades
    model = LinearRegression().fit(X, y)
    prediction = model.predict([[hours]])[0]
    return jsonify({"grade": round(min(float(prediction), 100.0), 2)})

@app.route('/attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    sid = data.get('student_id')
    return jsonify({"message": f"Attendance mark ho gayi: {STUDENT_NAMES.get(sid, sid)}"})

@app.route('/get_data/<sid>')
def get_data(sid):
    return jsonify({"schedule": SCHEDULE_DB.get(sid, []), "tasks": TASKS_DB.get(sid, [])})

@app.route('/generate_qr/<sid>')
def generate_qr(sid):
    qr = qrcode.make(sid)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/performance_plot/<sid>')
def performance_plot(sid):
    plt.figure(figsize=(10, 4), facecolor='#1e293b')
    ax = plt.axes()
    ax.set_facecolor("#1e293b")
    weeks = np.arange(1, 6)
    scores = np.random.randint(70, 95, 5)
    plt.plot(weeks, scores, marker='o', color='#3b82f6', linewidth=3)
    plt.title(f"Growth: {sid}", color='white', fontweight='bold')
    plt.tick_params(colors='white')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
