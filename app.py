from flask import Flask, request, jsonify, send_file, render_template_string
import datetime
import qrcode
import io
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os

app = Flask(__name__)

# ==========================================
# CORE ENGINEERING DATABASES (Mock Data)
# ==========================================

STUDENTS = {
    "S001": {"name": "Alice Johnson", "branch": "CSE", "year": "3rd", "email": "alice.vit@university.edu"},
    "S002": {"name": "Bob Smith", "branch": "ECE", "year": "2nd", "email": "bob.ece@university.edu"},
    "S003": {"name": "Charlie Brown", "branch": "ME", "year": "4th", "email": "charlie.me@university.edu"},
    "S004": {"name": "Diana Prince", "branch": "EE", "year": "1st", "email": "diana.ee@university.edu"},
    "S005": {"name": "Ethan Hunt", "branch": "Civil", "year": "3rd", "email": "ethan.civ@university.edu"}
}

# Advanced Deadline Database [cite: 7, 62]
DEADLINES = {
    "S001": [
        {"task": "Compiler Design Lab Viva", "date": "2026-04-05", "priority": "High"},
        {"task": "DBMS Project Documentation", "date": "2026-04-10", "priority": "Medium"},
        {"task": "Machine Learning Assignment", "date": "2026-04-02", "priority": "Urgent"}
    ],
    "S002": [
        {"task": "VLSI Circuit Design Report", "date": "2026-04-07", "priority": "High"},
        {"task": "Microprocessor Assembly Code", "date": "2026-04-12", "priority": "Low"}
    ],
    "S003": [
        {"task": "Thermodynamics Problem Set", "date": "2026-04-03", "priority": "Urgent"},
        {"task": "CAD Design Submission", "date": "2026-04-15", "priority": "Medium"}
    ]
}

# Resource Library for Engineers [cite: 13, 25]
RESOURCES = [
    {"name": "NPTEL Video Lectures", "url": "https://nptel.ac.in/", "cat": "General"},
    {"name": "IEEE Xplore Journals", "url": "https://ieeexplore.ieee.org/", "cat": "Research"},
    {"name": "GeeksForGeeks CS Portal", "url": "https://www.geeksforgeeks.org/", "cat": "Coding"},
    {"name": "MIT OpenCourseWare", "url": "https://ocw.mit.edu/", "cat": "Core"},
    {"name": "Stack Overflow", "url": "https://stackoverflow.com/", "cat": "Debug"},
    {"name": "GitHub Education", "url": "https://education.github.com/", "cat": "Tools"}
]

# ==========================================
# UI TEMPLATE (HTML, CSS, JS) - 500+ Lines Focus
# ==========================================

HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Veyransh | Engineering OS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');
        
        :root {
            --bg: #0d1117;
            --card: #161b22;
            --border: #30363d;
            --accent: #58a6ff;
            --success: #238636;
            --danger: #da3633;
            --warning: #d29922;
        }

        body {
            background-color: var(--bg);
            color: #c9d1d9;
            font-family: 'JetBrains Mono', monospace;
            overflow-x: hidden;
            scroll-behavior: smooth;
        }

        .engg-container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }

        /* CUSTOM SCROLLBAR */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg); }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

        /* NEOMORPHIC CLASSES */
        .glass-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .glass-card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
        }

        .status-header {
            background: #010409;
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .btn-engg {
            background-color: #21262d;
            border: 1px solid var(--border);
            color: var(--accent);
            font-weight: 700;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 12px;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-engg:hover {
            background-color: var(--border);
            border-color: #8b949e;
        }

        .btn-success {
            background-color: var(--success);
            color: white;
            border: none;
        }

        .btn-success:hover { background-color: #2ea043; }

        input, select {
            background: #0d1117;
            border: 1px solid var(--border);
            color: white;
            padding: 12px;
            border-radius: 6px;
            outline: none;
            width: 100%;
        }

        input:focus { border-color: var(--accent); }

        .deadline-item {
            border-left: 4px solid var(--danger);
            background: #1c2128;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 0 8px 8px 0;
        }

        .priority-high { border-left-color: var(--danger); }
        .priority-medium { border-left-color: var(--warning); }
        .priority-low { border-left-color: var(--success); }

        /* ANIMATIONS */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .animate-ui { animation: fadeIn 0.5s ease forwards; }

        .timer-display {
            font-size: 3rem;
            font-weight: 800;
            color: var(--accent);
            text-shadow: 0 0 20px rgba(88, 166, 255, 0.3);
        }

        .log-box {
            font-size: 10px;
            color: #8b949e;
            height: 150px;
            overflow-y: auto;
            background: #010409;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid var(--border);
        }

        /* GRID LAYOUT */
        .grid-layout {
            display: grid;
            grid-template-columns: 300px 1fr 350px;
            gap: 20px;
        }

        @media (max-width: 1200px) {
            .grid-layout { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

    <header class="status-header p-4">
        <div class="engg-container flex justify-between items-center">
            <div class="flex items-center space-x-4">
                <div class="text-3xl bg-blue-600/20 p-2 rounded-lg border border-blue-500/50">⚙️</div>
                <div>
                    <h1 class="text-xl font-bold tracking-tighter">VEYRANSH <span class="text-sky-400">ENGG_SYSTEMS</span></h1>
                    <p class="text-[9px] text-gray-500 font-bold uppercase tracking-widest">Build: 2026.04.RC1 | Kernel: Optimized</p>
                </div>
            </div>
            <div class="flex space-x-10 text-right">
                <div class="hidden md:block">
                    <p class="text-[10px] text-gray-500 font-bold">SYSTEM_UPTIME</p>
                    <p id="uptime" class="text-xs font-bold text-emerald-400">00:00:00</p>
                </div>
                <div>
                    <p id="live-time" class="text-lg font-bold text-sky-400">--:--:--</p>
                    <p id="live-date" class="text-[9px] text-gray-500 font-bold uppercase"></p>
                </div>
            </div>
        </div>
    </header>

    <main class="engg-container mt-6">
        <div class="grid-layout">
            
            <section class="space-y-6">
                <div class="glass-card p-6 animate-ui">
                    <h3 class="text-xs font-bold text-gray-500 uppercase mb-4 tracking-widest border-b border-gray-800 pb-2">
                        <i class="fa-solid fa-fingerprint mr-2"></i> User Session
                    </h3>
                    <div class="space-y-4">
                        <div>
                            <label class="text-[9px] text-gray-400 font-bold mb-1 block">SELECT ENGINEER</label>
                            <select id="student-selector">
                                {% for id, info in students.items() %}
                                <option value="{{ id }}">{{ id }} - {{ info.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <button onclick="markAttendance()" class="btn-engg btn-success w-full">Mark Presence</button>
                        <div class="mt-4 p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg">
                            <p class="text-[10px] text-blue-400" id="session-info">Standby: Authenticate to start session.</p>
                        </div>
                    </div>
                </div>

                <div class="glass-card p-6 text-center animate-ui" style="animation-delay: 0.1s;">
                    <h3 class="text-xs font-bold text-gray-500 uppercase mb-4 tracking-widest">Verification QR</h3>
                    <div class="bg-white p-2 inline-block rounded-xl">
                        <img id="qr-image" src="/generate_qr/S001" class="w-32 h-32">
                    </div>
                    <p class="text-[9px] text-gray-500 mt-4">Scan for Library/Lab Access</p>
                </div>

                <div class="glass-card p-6 animate-ui" style="animation-delay: 0.2s;">
                    <h3 class="text-xs font-bold text-gray-500 uppercase mb-4 tracking-widest">Resource Hub</h3>
                    <div class="space-y-2">
                        {% for res in resources %}
                        <a href="{{ res.url }}" target="_blank" class="block p-3 bg-[#0d1117] rounded-lg border border-transparent hover:border-blue-500/50 transition-all group">
                            <div class="flex justify-between items-center">
                                <span class="text-[10px] font-bold group-hover:text-blue-400">{{ res.name }}</span>
                                <span class="text-[8px] bg-gray-800 px-2 py-0.5 rounded text-gray-400 uppercase">{{ res.cat }}</span>
                            </div>
                        </a>
                        {% endfor %}
                    </div>
                </div>
            </section>

            <section class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="glass-card p-6 animate-ui" style="animation-delay: 0.3s;">
                        <h3 class="text-xs font-bold text-blue-400 uppercase mb-4 flex items-center">
                            <i class="fa-solid fa-brain mr-2"></i> SGPA Predictor
                        </h3>
                        <div class="space-y-4">
                            <p class="text-[10px] text-gray-500">ML Model: Based on your average study hours/day.</p>
                            <input type="number" id="study-hours" placeholder="Study Hours (e.g. 8)" min="1" max="24">
                            <button onclick="predictSGPA()" class="btn-engg w-full bg-blue-600/10 border-blue-500/50 text-blue-400">Compute Result</button>
                            <div id="sgpa-result" class="text-center font-bold text-2xl text-emerald-400 hidden">
                                SGPA: 8.5
                            </div>
                        </div>
                    </div>

                    <div class="glass-card p-6 animate-ui" style="animation-delay: 0.4s;">
                        <h3 class="text-xs font-bold text-orange-400 uppercase mb-4 flex items-center">
                            <i class="fa-solid fa-clock mr-2"></i> Deep Work Session
                        </h3>
                        <div class="text-center">
                            <div id="timer" class="timer-display mb-4">25:00</div>
                            <div class="flex space-x-2">
                                <button onclick="toggleTimer()" id="timer-btn" class="btn-engg flex-1">Start</button>
                                <button onclick="resetTimer()" class="btn-engg"><i class="fa-solid fa-rotate-right"></i></button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="glass-card p-6 animate-ui" style="animation-delay: 0.5s;">
                    <div class="flex justify-between items-center mb-6">
                        <h3 class="text-xs font-bold text-gray-500 uppercase">
                            <i class="fa-solid fa-chart-line mr-2"></i> Attendance & Engagement Analytics
                        </h3>
                        <div class="flex space-x-2">
                            <span class="w-3 h-3 bg-blue-500 rounded-full inline-block"></span>
                            <span class="text-[9px] text-gray-500 uppercase font-bold">Attendance %</span>
                        </div>
                    </div>
                    <div class="relative w-full rounded-xl overflow-hidden bg-[#0d1117] border border-gray-800">
                        <img id="analytics-chart" src="/performance_plot/S001" class="w-full h-auto opacity-90">
                    </div>
                </div>

                <div class="glass-card p-6 animate-ui" style="animation-delay: 0.6s;">
                    <h3 class="text-xs font-bold text-gray-500 uppercase mb-4">System Console Logs</h3>
                    <div id="console-logs" class="log-box custom-scroll">
                        <p class="mb-1 text-emerald-500">> [SYSTEM] Boot sequence complete.</p>
                        <p class="mb-1">> [AUTH] Awaiting user login...</p>
                    </div>
                </div>
            </section>

            <section class="space-y-6">
                <div class="glass-card p-6 animate-ui" style="animation-delay: 0.7s; border-color: var(--danger);">
                    <h3 class="text-xs font-bold text-red-500 uppercase mb-6 tracking-widest flex justify-between">
                        <span><i class="fa-solid fa-fire mr-2"></i> Immediate Deadlines</span>
                        <span class="bg-red-500/20 text-[8px] px-2 py-0.5 rounded">URGENT</span>
                    </h3>
                    <div id="deadline-container" class="custom-scroll max-h-[400px] pr-2">
                        </div>
                </div>

                <div class="glass-card p-6 animate-ui" style="animation-delay: 0.8s;">
                    <h3 class="text-xs font-bold text-gray-500 uppercase mb-4 tracking-widest">Branch Stats</h3>
                    <div class="space-y-4">
                        <div class="space-y-1">
                            <div class="flex justify-between text-[9px] font-bold">
                                <span>Attendance Threshold</span>
                                <span class="text-emerald-400">75% (Safe)</span>
                            </div>
                            <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                                <div class="bg-emerald-500 h-full w-[75%] shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                            </div>
                        </div>
                        <div class="space-y-1">
                            <div class="flex justify-between text-[9px] font-bold">
                                <span>Syllabus Covered</span>
                                <span class="text-blue-400">40%</span>
                            </div>
                            <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                                <div class="bg-blue-500 h-full w-[40%] shadow-[0_0_10px_rgba(59,130,246,0.5)]"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="p-6 bg-blue-600/10 border border-blue-500/20 rounded-xl text-center">
                    <p class="text-[9px] font-bold text-blue-400 uppercase mb-2 italic">Engineering Tip:</p>
                    <p class="text-[10px] text-gray-400 font-medium">"Focus on standard documentation rather than scattered tutorials. RTFM."</p>
                </div>
            </section>
        </div>
    </main>

    <script>
        // CORE GLOBAL VARIABLES
        const selector = document.getElementById('student-selector');
        const logBox = document.getElementById('console-logs');
        const timerDisplay = document.getElementById('timer');
        let timerSeconds = 1500;
        let timerActive = false;
        let timerInterval;

        // UTILITY: ADD LOGS
        function addLog(msg, type = 'info') {
            const p = document.createElement('p');
            p.className = 'mb-1 ' + (type === 'success' ? 'text-emerald-500' : type === 'error' ? 'text-red-500' : 'text-gray-500');
            p.innerText = `> [${new Date().toLocaleTimeString()}] ${msg}`;
            logBox.prepend(p);
        }

        // CLOCK AND UPTIME
        function initClock() {
            const startTime = Date.now();
            setInterval(() => {
                const now = new Date();
                document.getElementById('live-time').innerText = now.toLocaleTimeString();
                document.getElementById('live-date').innerText = now.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
                
                const elapsed = Math.floor((Date.now() - startTime) / 1000);
                const h = Math.floor(elapsed / 3600).toString().padStart(2, '0');
                const m = Math.floor((elapsed % 3600) / 60).toString().padStart(2, '0');
                const s = (elapsed % 60).toString().padStart(2, '0');
                document.getElementById('uptime').innerText = `${h}:${m}:${s}`;
            }, 1000);
        }

        // POMODORO TIMER
        function toggleTimer() {
            if (timerActive) {
                clearInterval(timerInterval);
                document.getElementById('timer-btn').innerText = "Start";
                addLog("Deep work session paused.");
            } else {
                timerInterval = setInterval(() => {
                    timerSeconds--;
                    let mins = Math.floor(timerSeconds / 60);
                    let secs = timerSeconds % 60;
                    timerDisplay.innerText = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
                    if (timerSeconds <= 0) {
                        clearInterval(timerInterval);
                        alert("Session Complete! Take a break.");
                        resetTimer();
                    }
                }, 1000);
                document.getElementById('timer-btn').innerText = "Stop";
                addLog("Deep work session initialized.");
            }
            timerActive = !timerActive;
        }

        function resetTimer() {
            clearInterval(timerInterval);
            timerSeconds = 1500;
            timerDisplay.innerText = "25:00";
            document.getElementById('timer-btn').innerText = "Start";
            timerActive = false;
            addLog("Timer reset to 25:00.");
        }

        // ATTENDANCE LOGIC
        async function markAttendance() {
            const sid = selector.value;
            try {
                const res = await fetch('/attendance', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({student_id: sid})
                });
                const data = await res.json();
                addLog(`Attendance confirmed for ${sid}.`, 'success');
                document.getElementById('session-info').innerText = "Status: Present";
            } catch (e) {
                addLog("Connection to backend failed.", 'error');
            }
        }

        // ML SGPA PREDICTION
        async function predictSGPA() {
            const hours = document.getElementById('study-hours').value;
            if(!hours || hours < 0) {
                addLog("Invalid input for ML computation.", 'error');
                return;
            }
            addLog(`Analyzing study patterns for ${hours} hours/day...`);
            const res = await fetch(`/predict_grade?hours=${hours}`);
            const data = await res.json();
            const resultBox = document.getElementById('sgpa-result');
            resultBox.innerText = `PREDICTED SGPA: ${data.sgpa}`;
            resultBox.classList.remove('hidden');
            addLog(`Computation complete. Forecasted SGPA: ${data.sgpa}`, 'success');
        }

        // DASHBOARD REFRESH
        async function refreshDashboard(sid) {
            addLog(`Fetching data packets for student_id: ${sid}...`);
            document.getElementById('qr-image').src = `/generate_qr/${sid}`;
            document.getElementById('analytics-chart').src = `/performance_plot/${sid}?v=` + Date.now();
            
            const res = await fetch(`/get_data/${sid}`);
            const data = await res.json();
            
            const container = document.getElementById('deadline-container');
            container.innerHTML = data.deadlines.map(d => `
                <div class="deadline-item priority-${d.priority.toLowerCase()}">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-[10px] font-bold text-white">${d.task}</span>
                        <span class="text-[8px] bg-black/20 px-1 rounded">${d.priority}</span>
                    </div>
                    <p class="text-[8px] text-gray-400 italic"><i class="fa-regular fa-calendar mr-1"></i> Due: ${d.date}</p>
                </div>
            `).join('') || '<p class="text-[10px] text-gray-600 text-center py-10 italic">No pending tasks found in buffer.</p>';
            
            addLog("Dashboard buffer refreshed.", 'info');
        }

        // INITIALIZATION
        selector.addEventListener('change', (e) => refreshDashboard(e.target.value));
        initClock();
        refreshDashboard('S001');

    </script>
</body>
</html>
"""

# ==========================================
# BACKEND API SYSTEMS (Optimized Routes)
# ==========================================

@app.route('/')
def main_entry():
    """Renders the primary Engineering OS Dashboard."""
    return render_template_string(HTML_UI, students=STUDENTS, resources=RESOURCES)

@app.route('/predict_grade')
def api_predict_sgpa():
    """Uses Scikit-learn Linear Regression to forecast SGPA based on hours."""
    h = float(request.args.get('hours', 0))
    # Training Data: [[hours]], [sgpa]
    X_train = np.array([[2], [4], [6], [8], [10]]) 
    y_train = np.array([6.5, 7.2, 8.0, 8.8, 9.5])
    
    regressor = LinearRegression().fit(X_train, y_train)
    prediction = regressor.predict([[h]])[0]
    
    # Ensuring bound checks (0.0 to 10.0)
    final_sgpa = round(min(max(float(prediction), 0.0), 10.0), 2)
    return jsonify({"sgpa": final_sgpa})

@app.route('/get_data/<sid>')
def api_get_student_data(sid):
    """Retrieves deadline buffer for a specific student_id."""
    return jsonify({"deadlines": DEADLINES.get(sid, [])})

@app.route('/attendance', methods=['POST'])
def api_mark_attendance():
    """Logs student attendance with timestamp."""
    sid = request.json.get('student_id')
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if sid not in ATTENDANCE_DB: ATTENDANCE_DB[sid] = []
    ATTENDANCE_DB[sid].append(now)
    return jsonify({"status": "SUCCESS", "message": f"Verification for {sid} confirmed at {now}"})

@app.route('/generate_qr/<sid>')
def api_generate_qr(sid):
    """Generates a unique QR token for campus/lab authentication."""
    qr_code = qrcode.QRCode(version=1, border=2)
    qr_code.add_data(f"VEYRANSH_AUTH_{sid}")
    qr_code.make(fit=True)
    
    img = qr_code.make_image(fill_color="black", back_color="white")
    byte_io = io.BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')

@app.route('/performance_plot/<sid>')
def api_generate_chart(sid):
    """Generates a Matplotlib chart for attendance trends."""
    plt.figure(figsize=(12, 4), facecolor='#0d1117')
    ax = plt.axes()
    ax.set_facecolor("#0d1117")
    
    weeks = np.arange(1, 11)
    # Simulated attendance data with slight random fluctuations
    engagement = np.array([85, 88, 82, 90, 95, 92, 89, 94, 98, 96])
    
    plt.plot(weeks, engagement, color='#58a6ff', linewidth=3, marker='o', markersize=8, label='Attendance %')
    plt.fill_between(weeks, engagement, color='#58a6ff', alpha=0.1)
    
    plt.title(f"Analytical Engagement Trend: {sid}", color='white', fontsize=12, fontweight='bold', pad=20)
    plt.xlabel("Semester Week", color='#8b949e', fontsize=10)
    plt.ylabel("Attendance Status %", color='#8b949e', fontsize=10)
    
    plt.tick_params(colors='#8b949e', labelsize=8)
    plt.grid(color='#30363d', linestyle='--', linewidth=0.5, alpha=0.5)
    plt.ylim(0, 110)
    
    # Save to buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    img_buffer.seek(0)
    return send_file(img_buffer, mimetype='image/png')

if __name__ == '__main__':
    # Flask Application Launch
    app.run(host='0.0.0.0', port=5000, debug=True)
