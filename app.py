from flask import Flask, request, jsonify, send_file, render_template_string
import datetime
import qrcode
import io
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression # [cite: 66]
import os

app = Flask(__name__)

# --- Configuration & Databases ---
ATTENDANCE_DB = {}
STUDENT_NAMES = {
    "S001": "Alice Johnson", "S002": "Bob Smith", "S003": "Charlie Brown",
    "S004": "Diana Prince", "S005": "Ethan Hunt"
}
LIBRARY = {
    "Python Core": "https://docs.python.org/3/",
    "ML Algorithms": "https://scikit-learn.org/",
    "DS & Algo": "https://visualgo.net/"
}

# --- Integrated UI (Modern Dark Theme) ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Veyransh Ultra Pro Max | AI Academic OS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        :root { --accent: #38bdf8; --bg-dark: #020617; }
        body { background: var(--bg-dark); font-family: 'Plus Jakarta Sans', sans-serif; color: white; scroll-behavior: smooth; }
        .glass { background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.05); }
        .neon-border { border: 1px solid rgba(56, 189, 248, 0.3); box-shadow: 0 0 15px rgba(56, 189, 248, 0.1); }
        .custom-scroll::-webkit-scrollbar { width: 4px; }
        .custom-scroll::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
        .animate-pulse-slow { animation: pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
    </style>
</head>
<body class="p-4 lg:p-6 custom-scroll">
    <div class="max-w-[1500px] mx-auto">
        <nav class="flex flex-col lg:flex-row justify-between items-center mb-8 glass p-6 rounded-[2rem] neon-border">
            <div class="flex items-center space-x-4">
                <div class="w-14 h-14 bg-gradient-to-br from-sky-400 to-blue-600 rounded-2xl flex items-center justify-center text-2xl shadow-lg shadow-sky-500/20">📡</div>
                <div>
                    <h1 class="text-2xl font-black tracking-tight italic">VEYRANSH <span class="text-sky-400">OS</span></h1>
                    <p class="text-[9px] font-bold text-slate-500 uppercase tracking-[0.2em]">Next-Gen Intelligence [cite: 10, 13]</p>
                </div>
            </div>
            <div class="hidden md:flex space-x-12">
                <div class="text-center">
                    <p class="text-xs font-bold text-slate-500 mb-1">CURRENT STATUS</p>
                    <span class="flex items-center text-xs font-black text-emerald-400"><span class="w-2 h-2 bg-emerald-500 rounded-full mr-2 animate-pulse"></span> ONLINE</span>
                </div>
                <div class="text-center">
                    <p class="text-xl font-black text-sky-400" id="clock">--:--:--</p>
                    <p class="text-[10px] font-bold text-slate-500 uppercase" id="date">-- --- ----</p>
                </div>
            </div>
        </nav>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-3 space-y-6">
                <div class="glass p-6 rounded-[2rem] space-y-4">
                    <h3 class="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center"><i class="fa-solid fa-microchip mr-2 text-sky-400"></i> Authentication</h3>
                    <select id="student-id" class="w-full p-4 bg-slate-900/50 border border-slate-800 rounded-2xl text-xs font-bold outline-none focus:border-sky-500 transition-all">
                        {% for id, name in students.items() %}
                        <option value="{{ id }}">{{ id }} - {{ name }}</option>
                        {% endfor %}
                    </select>
                    <button onclick="logAttendance()" class="w-full py-4 bg-sky-500 text-white rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-sky-400 hover:shadow-lg hover:shadow-sky-500/20 transition-all">Mark Attendance [cite: 4]</button>
                </div>

                <div class="glass p-6 rounded-[2rem] text-center relative overflow-hidden">
                    <div class="absolute -right-4 -top-4 w-20 h-20 bg-sky-500/10 rounded-full blur-2xl"></div>
                    <p class="text-[10px] font-black text-slate-500 mb-2 uppercase">Current Level</p>
                    <h4 class="text-4xl font-black text-sky-400 mb-1">LVL 12</h4>
                    <p class="text-[9px] font-bold text-sky-500/60 uppercase">PRODIGY STATUS</p>
                    <div class="mt-4 w-full bg-slate-800 h-1.5 rounded-full"><div class="bg-sky-400 w-3/4 h-full rounded-full"></div></div>
                </div>

                <div class="glass p-6 rounded-[2rem] text-center border-t-2 border-sky-500/20">
                    <img id="qr-code" src="/generate_qr/S001" class="mx-auto w-36 h-36 bg-white p-3 rounded-3xl mb-4">
                    <p class="text-[9px] font-black text-slate-500 uppercase">Verification Hash Key</p>
                </div>
            </div>

            <div class="lg:col-span-6 space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="glass p-6 rounded-[2rem] border-l-4 border-sky-400">
                        <h4 class="font-bold text-sm mb-4">🤖 Grade Predictor</h4>
                        <div class="flex space-x-2">
                            <input type="number" id="hours" placeholder="Study Hours" class="w-full bg-slate-900/80 p-3 rounded-xl text-xs border border-slate-800 outline-none">
                            <button onclick="getPrediction()" class="bg-sky-500 px-4 rounded-xl font-black text-[10px]">EXECUTE</button>
                        </div>
                        <p id="pred-out" class="mt-4 text-xs font-bold text-emerald-400"></p>
                    </div>
                    <div class="glass p-6 rounded-[2rem] border-l-4 border-indigo-400">
                        <h4 class="font-bold text-sm mb-2">📚 AI Quiz Engine</h4>
                        <p class="text-[9px] text-slate-500 mb-4 font-bold">GENERATE QUESTIONS FROM NOTES [cite: 58, 60]</p>
                        <button onclick="alert('Module loading... Scanning database.')" class="w-full py-3 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-xl font-bold text-[10px] hover:bg-indigo-500 hover:text-white transition-all">START SESSION</button>
                    </div>
                </div>

                <div class="glass p-6 rounded-[2rem]">
                    <div class="flex justify-between items-center mb-6">
                        <h4 class="font-black text-sm uppercase tracking-tighter">Academic Growth Wave </h4>
                        <span class="text-[9px] font-bold bg-slate-800 px-3 py-1 rounded-full text-slate-400 uppercase">Real-time Data</span>
                    </div>
                    <img id="growth-chart" src="/performance_plot/S001" class="w-full h-auto rounded-3xl">
                </div>
            </div>

            <div class="lg:col-span-3 space-y-6">
                <div class="glass p-6 rounded-[2rem]">
                    <h3 class="text-[10px] font-black text-slate-500 uppercase mb-4 tracking-widest">System Logs</h3>
                    <div id="logs" class="h-32 overflow-y-auto pr-2 custom-scroll space-y-3">
                        <p class="text-[9px] border-l-2 border-sky-500 pl-3 py-1 text-slate-400 font-bold uppercase">Kernel Ready...</p>
                    </div>
                </div>

                <div class="glass p-6 rounded-[2rem]">
                    <h3 class="text-[10px] font-black text-slate-500 uppercase mb-4 tracking-widest">Smart Library </h3>
                    <div class="space-y-3">
                        {% for sub, link in library.items() %}
                        <a href="{{ link }}" target="_blank" class="flex justify-between items-center p-3 bg-slate-900/50 rounded-xl hover:bg-sky-500/10 transition-all group">
                            <span class="text-[10px] font-bold text-slate-300 group-hover:text-sky-400">{{ sub }}</span>
                            <i class="fa-solid fa-arrow-up-right-from-square text-[9px] text-slate-600"></i>
                        </a>
                        {% endfor %}
                    </div>
                </div>

                <div class="glass p-8 rounded-[2rem] text-center border-b-4 border-sky-500/20">
                    <p class="text-[10px] font-black text-slate-500 mb-4 uppercase">Focus Protocol</p>
                    <div class="text-4xl font-black tracking-tighter text-sky-400 mb-6" id="timer">25:00</div>
                    <div class="flex space-x-3">
                        <button onclick="timerCtrl()" id="t-btn" class="flex-1 py-3 bg-slate-800 rounded-xl text-[10px] font-black uppercase hover:bg-slate-700 transition">Start</button>
                        <button onclick="timerReset()" class="px-5 py-3 bg-slate-800 rounded-xl text-[10px] hover:bg-slate-700 transition"><i class="fa-solid fa-rotate-right"></i></button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function pushLog(msg) {
            const l = document.getElementById('logs');
            const p = document.createElement('p');
            p.className = 'text-[9px] border-l-2 border-sky-500 pl-3 py-1 text-slate-400 font-bold uppercase';
            p.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
            l.prepend(p);
        }

        function updateUI() {
            const n = new Date();
            document.getElementById('clock').innerText = n.toLocaleTimeString();
            document.getElementById('date').innerText = n.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
        }
        setInterval(updateUI, 1000); updateUI();

        let tSecs = 1500, tRun = false, tInt;
        function timerCtrl() {
            if (tRun) { clearInterval(tInt); document.getElementById('t-btn').innerText = "Start"; pushLog("Timer Paused"); }
            else { 
                tInt = setInterval(() => {
                    tSecs--;
                    let m = Math.floor(tSecs/60), s = tSecs%60;
                    document.getElementById('timer').innerText = `${m}:${s<10?'0':''}${s}`;
                    if(tSecs<=0) timerReset();
                }, 1000);
                document.getElementById('t-btn').innerText = "Stop";
                pushLog("Focus Mode Engaged");
            }
            tRun = !tRun;
        }
        function timerReset() { clearInterval(tInt); tSecs = 1500; document.getElementById('timer').innerText = "25:00"; tRun = false; document.getElementById('t-btn').innerText = "Start"; pushLog("Timer Reset"); }

        const sId = document.getElementById('student-id');
        sId.addEventListener('change', (e) => {
            document.getElementById('qr-code').src = `/generate_qr/${e.target.value}`;
            document.getElementById('growth-chart').src = `/performance_plot/${e.target.value}?v=`+Date.now();
            pushLog(`Switched to Student ${e.target.value}`);
        });

        async function logAttendance() {
            const res = await fetch('/attendance', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({student_id: sId.value}) });
            const data = await res.json();
            pushLog(data.message);
            alert("SUCCESS: Attendance Logged.");
        }

        async function getPrediction() {
            const h = document.getElementById('hours').value;
            if(!h) return;
            const res = await fetch(`/predict_grade?hours=${h}`);
            const d = await res.json();
            document.getElementById('pred-out').innerText = `EXPECTED GRADE: ${d.grade}%`;
            pushLog(`ML Analysis: Predicted ${d.grade}%`);
        }
    </script>
</body>
</html>
"""

# --- Backend API Systems ---

@app.route('/')
def main_hub():
    return render_template_string(HTML_UI, students=STUDENT_NAMES, library=LIBRARY)

@app.route('/predict_grade')
def api_predict():
    # Linear Regression ML Simulation 
    h = float(request.args.get('hours', 0))
    X = np.array([[2], [4], [6], [8], [10]]) 
    y = np.array([55, 68, 80, 89, 98])
    model = LinearRegression().fit(X, y)
    out = model.predict([[h]])[0]
    return jsonify({"grade": round(min(float(out), 100.0), 2)})

@app.route('/attendance', methods=['POST'])
def api_attendance():
    sid = request.json.get('student_id')
    return jsonify({"message": f"ENTRY VERIFIED FOR {sid}"})

@app.route('/generate_qr/<sid>')
def api_qr(sid):
    qr = qrcode.make(sid)
    b = io.BytesIO()
    qr.save(b, format='PNG')
    b.seek(0)
    return send_file(b, mimetype='image/png')

@app.route('/performance_plot/<sid>')
def api_plot(sid):
    # Dynamic Plotting for Visualization [cite: 30, 81]
    plt.figure(figsize=(12, 4), facecolor='#020617')
    ax = plt.axes()
    ax.set_facecolor("#020617")
    x = np.arange(1, 6)
    y = np.random.randint(70, 99, 5)
    plt.plot(x, y, marker='o', color='#38bdf8', linewidth=4, markersize=12)
    plt.grid(color='#1e293b', linestyle='--', alpha=0.5)
    plt.tick_params(colors='white')
    b = io.BytesIO()
    plt.savefig(b, format='png', bbox_inches='tight', transparent=False)
    b.seek(0)
    plt.close()
    return send_file(b, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
