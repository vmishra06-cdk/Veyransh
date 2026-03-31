from flask import Flask, request, jsonify, send_file, render_template_string
import datetime
import io
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os

app = Flask(__name__)

# ==========================================
# 1. CORE ARCHITECTURE (In-Memory Storage)
# ==========================================

# In a real app, these would be in a database (SQL/NoSQL)
USER_DATA = {
    "deadlines": [
        {"task": "Compiler Design Project", "date": "2026-04-10", "priority": "Urgent"},
        {"task": "LeetCode 50 Days Challenge", "date": "2026-05-01", "priority": "High"}
    ],
    "resources": [
        {"name": "My Repo", "url": "https://github.com/", "icon": "fa-github"},
        {"name": "LeetCode", "url": "https://leetcode.com/", "icon": "fa-code"}
    ],
    "tasks": [],
    "performance": [75, 82, 80, 85, 90] # Points for Graph
}

# VIT Inspired Grade Mapping
GRADE_POINTS = {"S": 10, "A": 9, "B": 8, "C": 7, "D": 6, "E": 5, "F": 0}

# ==========================================
# 2. UI ENGINE (Tailwind + Custom CSS)
# ==========================================

HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Veyransh CS_OS | Developer Workspace</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Inter:wght@400;700&display=swap');
        
        :root {
            --bg: #050505;
            --card: #0f0f0f;
            --border: #1f1f1f;
            --accent: #3b82f6;
            --terminal: #121212;
        }

        body {
            background-color: var(--bg);
            color: #e2e8f0;
            font-family: 'Inter', sans-serif;
            scroll-behavior: smooth;
        }

        .code-font { font-family: 'Fira Code', monospace; }

        .glass-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            transition: all 0.3s ease;
        }

        .glass-card:hover { border-color: var(--accent); box-shadow: 0 0 20px rgba(59, 130, 246, 0.1); }

        .btn-primary {
            background: var(--accent);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }

        .btn-primary:hover { opacity: 0.9; transform: scale(1.02); }

        .input-dark {
            background: #161616;
            border: 1px solid var(--border);
            color: white;
            padding: 10px;
            border-radius: 8px;
            outline: none;
            width: 100%;
        }

        .input-dark:focus { border-color: var(--accent); }

        /* CUSTOM SCROLLBAR */
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }

        /* LOGO GRID */
        .platform-icon {
            font-size: 24px;
            transition: transform 0.2s;
        }
        .platform-icon:hover { transform: translateY(-3px); color: var(--accent); }
    </style>
</head>
<body class="p-4 lg:p-6">

    <header class="flex justify-between items-center mb-10 px-4">
        <div class="flex items-center space-x-4">
            <div class="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center text-2xl shadow-lg">💻</div>
            <div>
                <h1 class="text-xl font-bold tracking-tighter code-font">VEYRANSH <span class="text-blue-500">CS_OS</span></h1>
                <p class="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Environment: Development | Role: Software Engineer</p>
            </div>
        </div>
        <div class="text-right flex items-center space-x-6">
            <div class="hidden md:block">
                <p id="live-clock" class="text-lg font-bold code-font text-blue-400">--:--:--</p>
                <p id="live-date" class="text-[10px] text-gray-500 uppercase font-bold"></p>
            </div>
            <button onclick="toggleAI()" class="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center hover:bg-indigo-500 transition shadow-lg shadow-indigo-500/20">
                <i class="fa-solid fa-robot"></i>
            </button>
        </div>
    </header>

    <main class="grid grid-cols-1 lg:grid-cols-12 gap-6 max-w-[1600px] mx-auto">
        
        <section class="lg:col-span-3 space-y-6">
            <div class="glass-card p-6">
                <h3 class="text-xs font-bold text-gray-500 uppercase mb-6 tracking-widest">Quick Access</h3>
                <div class="grid grid-cols-4 gap-6 text-center">
                    <a href="https://leetcode.com/" target="_blank" class="platform-icon"><i class="fa-solid fa-code"></i><p class="text-[8px] mt-1 uppercase">LeetCode</p></a>
                    <a href="https://github.com/" target="_blank" class="platform-icon"><i class="fa-brands fa-github"></i><p class="text-[8px] mt-1 uppercase">GitHub</p></a>
                    <a href="https://hackerrank.com/" target="_blank" class="platform-icon"><i class="fa-brands fa-hackerrank"></i><p class="text-[8px] mt-1 uppercase">Rank</p></a>
                    <a href="https://stackoverflow.com/" target="_blank" class="platform-icon"><i class="fa-brands fa-stack-overflow"></i><p class="text-[8px] mt-1 uppercase">Stack</p></a>
                </div>
            </div>

            <div class="glass-card p-6">
                <h3 class="text-xs font-bold text-gray-500 uppercase mb-4 tracking-widest">Add Custom Resource</h3>
                <div class="space-y-3">
                    <input type="text" id="res-name" placeholder="Name (e.g. My Portfolio)" class="input-dark text-xs">
                    <input type="text" id="res-url" placeholder="URL (https://...)" class="input-dark text-xs">
                    <button onclick="addResource()" class="btn-primary w-full text-[10px]">SAVE LINK</button>
                </div>
                <div id="dynamic-resources" class="mt-4 space-y-2">
                    </div>
            </div>

            <div class="p-6 bg-orange-600/10 border border-orange-500/20 rounded-2xl flex items-center justify-between">
                <div>
                    <h4 class="text-xs font-bold text-orange-400">LeetCode Streak</h4>
                    <p class="text-[10px] text-gray-400">Daily problem is pending!</p>
                </div>
                <a href="https://leetcode.com/problemset/all/" target="_blank" class="text-orange-500 hover:scale-110 transition"><i class="fa-solid fa-fire text-2xl"></i></a>
            </div>
        </section>

        <section class="lg:col-span-6 space-y-6">
            <div class="glass-card p-6">
                <h3 class="text-xs font-bold text-blue-400 uppercase mb-4 flex items-center">
                    <i class="fa-solid fa-calculator mr-2"></i> VIT SGPA Estimator
                </h3>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="text-[9px] text-gray-500 font-bold uppercase mb-1 block">Course Credits</label>
                        <input type="number" id="credits" value="4" class="input-dark">
                    </div>
                    <div>
                        <label class="text-[9px] text-gray-500 font-bold uppercase mb-1 block">Target Grade</label>
                        <select id="grade" class="input-dark">
                            <option value="10">S (10)</option>
                            <option value="9">A (9)</option>
                            <option value="8">B (8)</option>
                            <option value="7">C (7)</option>
                        </select>
                    </div>
                </div>
                <button onclick="predictSGPA()" class="btn-primary w-full mt-4 text-[10px]">RUN ML SIMULATION</button>
                <div id="sgpa-out" class="mt-4 text-center font-bold text-2xl text-emerald-400 hidden"></div>
            </div>

            <div class="glass-card p-6">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xs font-bold text-gray-500 uppercase tracking-widest">Productivity Trend</h3>
                    <button onclick="updateGraph()" class="text-blue-500 text-xs"><i class="fa-solid fa-arrows-rotate"></i></button>
                </div>
                <div class="bg-black/40 rounded-xl border border-white/5 overflow-hidden">
                    <img id="main-chart" src="/get_plot" class="w-full h-auto">
                </div>
            </div>

            <div class="glass-card p-6">
                <h3 class="text-xs font-bold text-gray-500 uppercase mb-4 tracking-widest">Daily Task Planner</h3>
                <div class="flex space-x-2 mb-4">
                    <input type="text" id="new-task" placeholder="e.g. Finish React Hooks" class="input-dark">
                    <button onclick="addTask()" class="btn-primary px-6"><i class="fa-solid fa-plus"></i></button>
                </div>
                <div id="task-list" class="space-y-2 max-h-40 overflow-y-auto pr-2">
                    </div>
            </div>
        </section>

        <section class="lg:col-span-3 space-y-6">
            <div class="glass-card p-6 border-l-4 border-red-500">
                <h3 class="text-xs font-bold text-red-500 uppercase mb-4 flex justify-between items-center">
                    <span>Deadlines</span>
                    <button onclick="showDeadlineModal()" class="text-[10px] bg-red-500/10 px-2 py-1 rounded">+ Add</button>
                </h3>
                <div id="deadline-list" class="space-y-3">
                    </div>
            </div>

            <div class="bg-black border border-white/5 p-4 rounded-xl font-mono text-[10px] h-48 overflow-y-auto shadow-inner">
                <p class="text-emerald-500">> [SYSTEM] Booting CS_OS Kernel...</p>
                <p class="text-gray-500">> [LOG] Developer Authenticated.</p>
                <div id="terminal-logs"></div>
            </div>
        </section>
    </main>

    <div id="d-modal" class="fixed inset-0 bg-black/80 hidden items-center justify-center z-50 p-4">
        <div class="glass-card p-8 max-w-sm w-full">
            <h2 class="text-lg font-bold mb-4">New Deadline</h2>
            <input type="text" id="d-task" placeholder="Task Name" class="input-dark mb-3">
            <input type="date" id="d-date" class="input-dark mb-4">
            <div class="flex space-x-2">
                <button onclick="saveDeadline()" class="btn-primary flex-1">Save</button>
                <button onclick="toggleAI()" class="btn-engg flex-1 bg-gray-800 rounded-lg text-xs">Cancel</button>
            </div>
        </div>
    </div>

    <script>
        // CORE JS LOGIC
        function updateTime() {
            const now = new Date();
            document.getElementById('live-clock').innerText = now.toLocaleTimeString();
            document.getElementById('live-date').innerText = now.toLocaleDateString('en-US', {weekday:'short', month:'short', day:'numeric'});
        }
        setInterval(updateTime, 1000); updateTime();

        function addTerminalLog(msg) {
            const div = document.getElementById('terminal-logs');
            const p = document.createElement('p');
            p.className = 'text-gray-400 mt-1';
            p.innerText = `> [${new Date().toLocaleTimeString()}] ${msg}`;
            div.prepend(p);
        }

        // RESOURCE MANAGEMENT
        async function addResource() {
            const name = document.getElementById('res-name').value;
            const url = document.getElementById('res-url').value;
            if(!name || !url) return;
            const res = await fetch('/add_resource', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, url})
            });
            loadResources();
            addTerminalLog(`Added resource: ${name}`);
        }

        async function loadResources() {
            const res = await fetch('/get_resources');
            const data = await res.json();
            const div = document.getElementById('dynamic-resources');
            div.innerHTML = data.map(r => `
                <a href="${r.url}" target="_blank" class="flex justify-between items-center p-2 bg-white/5 rounded-lg border border-white/5 hover:border-blue-500 transition">
                    <span class="text-[10px] font-bold">${r.name}</span>
                    <i class="fa-solid fa-arrow-up-right-from-square text-[8px] text-gray-500"></i>
                </a>
            `).join('');
        }

        // SGPA PREDICTION
        function predictSGPA() {
            const credit = document.getElementById('credits').value;
            const gradeVal = document.getElementById('grade').value;
            const res = (credit * gradeVal) / credit; // Simple Logic for VIT
            const out = document.getElementById('sgpa-out');
            out.innerText = `ESTIMATED SGPA: ${res.toFixed(2)}`;
            out.classList.remove('hidden');
            addTerminalLog(`Calculated predicted SGPA: ${res}`);
        }

        // TASK MANAGER
        function addTask() {
            const val = document.getElementById('new-task').value;
            if(!val) return;
            const div = document.getElementById('task-list');
            div.innerHTML += `
                <div class="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/5 group">
                    <span class="text-xs">${val}</span>
                    <button class="text-red-500 opacity-0 group-hover:opacity-100 transition"><i class="fa-solid fa-trash-can"></i></button>
                </div>
            `;
            document.getElementById('new-task').value = "";
            addTerminalLog(`New task added: ${val}`);
        }

        // DEADLINE MODAL
        function showDeadlineModal() { document.getElementById('d-modal').classList.remove('hidden'); document.getElementById('d-modal').classList.add('flex'); }
        function toggleAI() { document.getElementById('d-modal').classList.add('hidden'); }

        async function saveDeadline() {
            const task = document.getElementById('d-task').value;
            const date = document.getElementById('d-date').value;
            await fetch('/add_deadline', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task, date, priority: 'High'})
            });
            loadDeadlines();
            toggleAI();
            addTerminalLog(`Deadline set: ${task}`);
        }

        async function loadDeadlines() {
            const res = await fetch('/get_deadlines');
            const data = await res.json();
            document.getElementById('deadline-list').innerHTML = data.map(d => `
                <div class="p-3 bg-white/5 rounded-xl mb-2 border-l-2 border-red-500">
                    <p class="text-[10px] font-bold">${d.task}</p>
                    <p class="text-[8px] text-gray-500 italic">${d.date}</p>
                </div>
            `).join('');
        }

        function updateGraph() {
            document.getElementById('main-chart').src = '/get_plot?v=' + Date.now();
            addTerminalLog("Graph re-rendered from data buffer.");
        }

        // INITIAL LOAD
        loadResources();
        loadDeadlines();
    </script>
</body>
</html>
"""

# ==========================================
# 3. BACKEND ROUTES (Full Functionality)
# ==========================================

@app.route('/')
def index():
    return render_template_string(HTML_UI)

@app.route('/get_resources')
def get_resources():
    return jsonify(USER_DATA['resources'])

@app.route('/add_resource', methods=['POST'])
def add_resource():
    data = request.json
    USER_DATA['resources'].append({"name": data['name'], "url": data['url'], "icon": "fa-link"})
    return jsonify({"status": "success"})

@app.route('/get_deadlines')
def get_deadlines():
    return jsonify(USER_DATA['deadlines'])

@app.route('/add_deadline', methods=['POST'])
def add_deadline():
    data = request.json
    USER_DATA['deadlines'].append(data)
    # Append points for the graph whenever a deadline is added
    USER_DATA['performance'].append(USER_DATA['performance'][-1] + np.random.randint(-5, 10))
    return jsonify({"status": "success"})

@app.route('/get_plot')
def get_plot():
    """Generates a Matplotlib plot based on User's productivity points."""
    plt.figure(figsize=(10, 4), facecolor='#0f0f0f')
    ax = plt.axes()
    ax.set_facecolor("#0f0f0f")
    
    data = np.array(USER_DATA['performance'])
    x = np.arange(len(data))
    
    plt.plot(x, data, color='#3b82f6', linewidth=3, marker='o', markersize=6)
    plt.fill_between(x, data, color='#3b82f6', alpha=0.1)
    
    plt.title("Development Productivity Index", color='white', fontsize=12, fontweight='bold', pad=20)
    plt.tick_params(colors='#444', labelsize=8)
    plt.grid(color='#1f1f1f', linestyle='--')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
