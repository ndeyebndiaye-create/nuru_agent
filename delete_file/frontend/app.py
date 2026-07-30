"""
NURU - Interface Finale
- Page d'accueil : Élève / Enseignant
- Espace Élève : Un seul chat pour tout (cours, exercices, quiz)
- Espace Enseignant : Tableau de bord
"""
from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)
API_URL = os.getenv("API_URL", "http://localhost:8080")

# ========================================
# PAGE D'ACCUEIL
# ========================================
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>NURU - Tuteur IA Sénégalais</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            background: linear-gradient(135deg, #f5f7fa 0%, #e8edf5 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            width: 100%;
            background: white;
            border-radius: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
            padding: 40px;
        }
        .header { text-align: center; padding: 20px 0; }
        .header .logo { font-size: 3rem; }
        .header h1 {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #00853F, #FDE100, #D63031);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .flag {
            display: flex;
            height: 6px;
            width: 200px;
            margin: 10px auto;
            border-radius: 3px;
            overflow: hidden;
        }
        .flag .green { flex: 1; background: #00853F; }
        .flag .yellow { flex: 1; background: #FDE100; }
        .flag .red { flex: 1; background: #D63031; }
        .subtitle { color: #636E72; font-size: 1.1rem; margin: 10px 0; }
        .cards {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 30px;
        }
        .card {
            padding: 40px 30px;
            border-radius: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid #E9ECEF;
            text-decoration: none;
            display: block;
            background: white;
        }
        .card:hover { transform: translateY(-10px); box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
        .card .icon { font-size: 4rem; }
        .card h2 { font-size: 1.5rem; color: #2D3436; margin: 10px 0; }
        .card p { color: #636E72; }
        .card .badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 15px;
        }
        .card-eleve { border-color: #00B894; }
        .card-eleve .badge { background: #00B894; color: white; }
        .card-profs { border-color: #FDCB6E; }
        .card-profs .badge { background: #FDCB6E; color: #2D3436; }
        .footer { text-align:center; margin-top:30px; color:#B2BEC3; font-size:0.8rem; }
        @media (max-width: 768px) {
            .cards { grid-template-columns: 1fr; }
            .container { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🇸🇳</div>
            <h1>NURU</h1>
            <div class="flag"><div class="green"></div><div class="yellow"></div><div class="red"></div></div>
            <div class="subtitle">Tuteur IA · Programme Sénégalais</div>
            <p style="color: #636E72; max-width: 600px; margin: 15px auto;">
                Accompagnement personnalisé en Mathématiques (Sénégal). Bienvenue ! Je suis Nuru, ton tuteur intelligent local.
            </p>
        </div>
        <div class="cards">
            <a href="/eleve" class="card card-eleve">
                <div class="icon">👨‍🎓</div>
                <h2>ESPACE ÉLÈVE</h2>
                <p>Pose des questions, fais des exercices et quiz</p>
                <span class="badge">📚 Accéder</span>
            </a>
            <a href="/prof" class="card card-profs">
                <div class="icon">👨‍🏫</div>
                <h2>ESPACE ENSEIGNANT</h2>
                <p>Suis les progrès de tes élèves</p>
                <span class="badge">📊 Tableau de bord</span>
            </a>
        </div>
        <div class="footer">🇸🇳 NURU - Tuteur IA pour l'Éducation au Sénégal</div>
    </div>
</body>
</html>
"""

# ========================================
# ESPACE ÉLÈVE - UN SEUL CHAT
# ========================================
ELEVE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>NURU - Espace Élève</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            padding: 20px 25px;
            background: white;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .header-left {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .header-left .logo { font-size: 2rem; }
        .header-left h1 {
            font-size: 1.3rem;
            color: #2D3436;
        }
        .header-left h1 span.green { color: #00853F; }
        .header-left h1 span.yellow { color: #FDE100; }
        .header-left h1 span.red { color: #D63031; }
        .flag {
            display: flex;
            height: 4px;
            width: 80px;
            border-radius: 2px;
            overflow: hidden;
            margin-top: 3px;
        }
        .flag .green { flex: 1; background: #00853F; }
        .flag .yellow { flex: 1; background: #FDE100; }
        .flag .red { flex: 1; background: #D63031; }
        .badge {
            display: inline-block;
            padding: 3px 12px;
            border-radius: 15px;
            font-size: 0.65rem;
            font-weight: 600;
            margin: 0 3px;
        }
        .badge.green { background: #00B894; color: white; }
        .badge.yellow { background: #FDCB6E; color: #2D3436; }
        .back-btn {
            padding: 6px 15px;
            border: 2px solid #E9ECEF;
            border-radius: 8px;
            background: white;
            color: #636E72;
            text-decoration: none;
            font-size: 0.85rem;
        }
        .back-btn:hover { background: #f5f5f5; }
        .status {
            font-size: 0.75rem;
            padding: 3px 12px;
            border-radius: 15px;
        }
        .status.online { background: #00B89420; color: #00B894; }
        .status.offline { background: #D6303120; color: #D63031; }
        .chat-box {
            height: 420px;
            overflow-y: auto;
            padding: 20px;
            background: #F8F9FA;
        }
        .message {
            padding: 12px 18px;
            margin: 8px 0;
            border-radius: 15px;
            max-width: 85%;
            word-wrap: break-word;
            animation: fadeIn 0.3s ease;
            line-height: 1.6;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            background: #DFE6E9;
            color: #2D3436;
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }
        .message.assistant {
            background: linear-gradient(135deg, #FDCB6E, #FDE100);
            color: #2D3436;
            margin-right: auto;
            border-bottom-left-radius: 4px;
            box-shadow: 0 2px 10px rgba(253, 203, 110, 0.2);
        }
        .message .time {
            font-size: 0.6rem;
            opacity: 0.5;
            display: block;
            margin-top: 5px;
        }
        .message .sources {
            font-size: 0.75rem;
            color: #636E72;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(99, 110, 114, 0.2);
        }
        .message .sources strong { color: #2D3436; }
        .input-area {
            padding: 15px 20px;
            background: white;
            border-top: 1px solid #E9ECEF;
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #DFE6E9;
            border-radius: 12px;
            font-size: 0.95rem;
            outline: none;
            font-family: inherit;
            transition: border-color 0.3s ease;
        }
        .input-area input:focus { border-color: #FDCB6E; }
        .input-area button {
            padding: 12px 28px;
            background: linear-gradient(135deg, #00853F, #00B894);
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .input-area button:hover { transform: scale(1.02); box-shadow: 0 4px 15px rgba(0,133,63,0.3); }
        .input-area button:disabled { opacity: 0.6; cursor: not-allowed; }
        .quick-questions {
            padding: 10px 20px;
            background: #F8F9FA;
            border-top: 1px solid #E9ECEF;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .quick-questions button {
            background: white;
            border: 2px solid #E9ECEF;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            color: #2D3436;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: inherit;
        }
        .quick-questions button:hover {
            border-color: #FDCB6E;
            background: #FFFBF0;
            transform: translateY(-2px);
        }
        .footer {
            text-align: center;
            padding: 12px 20px;
            background: white;
            border-top: 1px solid #E9ECEF;
            font-size: 0.75rem;
            color: #B2BEC3;
        }
        @media (max-width: 600px) {
            .header { flex-direction: column; align-items: flex-start; }
            .quick-questions { gap: 5px; }
            .quick-questions button { font-size: 0.7rem; padding: 4px 10px; }
            .message { max-width: 95%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-left">
                <div class="logo">🇸🇳</div>
                <div>
                    <h1><span class="green">N</span><span class="yellow">U</span><span class="red">R</span><span class="green">U</span></h1>
                    <div class="flag">
                        <div class="green"></div>
                        <div class="yellow"></div>
                        <div class="red"></div>
                    </div>
                </div>
                <span class="badge green">👨‍🎓 Élève</span>
                <span class="badge yellow">🧮 Maths</span>
            </div>
            <div>
                <span class="status" id="status">🔄 Connexion...</span>
                <a href="/" class="back-btn">🏠 Accueil</a>
            </div>
        </div>
        
        <div class="chat-box" id="chatBox">
            <div class="message assistant">
                👋 <strong>Bonjour ! Je suis NURU</strong>, ton tuteur intelligent.<br><br>
                📚 Je t'accompagne en <strong>Mathématiques - Terminale S1/S2</strong>.<br><br>
                Pose-moi toutes tes questions :<br>
                • 📖 <strong>Cours</strong> : "Explique-moi les dérivées"<br>
                • ✏️ <strong>Exercices</strong> : "Donne-moi un exercice sur les suites"<br>
                • 📋 <strong>Quiz</strong> : "Fais-moi un quiz sur la trigonométrie"<br><br>
                <strong>Que souhaites-tu apprendre aujourd'hui ?</strong> 🚀
            </div>
        </div>
        
        <div class="quick-questions">
            <button onclick="sendQuick('Explique-moi les dérivées')">📐 Dérivées</button>
            <button onclick="sendQuick('Qu\'est-ce qu\'une fonction exponentielle ?')">📈 Exponentielle</button>
            <button onclick="sendQuick('Donne-moi un exercice sur les suites')">📊 Exercice suites</button>
            <button onclick="sendQuick('Fais-moi un quiz sur la trigonométrie')">📋 Quiz</button>
            <button onclick="sendQuick('Calcule la dérivée de f(x) = x² + 3x')">🧮 Calcul</button>
        </div>
        
        <div class="input-area">
            <input type="text" id="msgInput" placeholder="Pose ta question..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()" id="sendBtn">🚀 Envoyer</button>
        </div>
        
        <div class="footer">
            🇸🇳 NURU - Tuteur IA pour l'Éducation au Sénégal
        </div>
    </div>
    
    <script>
        // ========================================
        // STATUT DE L'API
        // ========================================
        async function checkStatus() {
            try {
                const r = await fetch('/api/health');
                const status = document.getElementById('status');
                if (r.ok) {
                    status.textContent = '🟢 Connecté';
                    status.className = 'status online';
                } else {
                    status.textContent = '🔴 Hors-ligne';
                    status.className = 'status offline';
                }
            } catch {
                document.getElementById('status').textContent = '🔴 Hors-ligne';
                document.getElementById('status').className = 'status offline';
            }
        }
        checkStatus();
        setInterval(checkStatus, 15000);
        
        // ========================================
        // CHAT
        // ========================================
        async function sendMessage() {
            const input = document.getElementById('msgInput');
            const msg = input.value.trim();
            if (!msg) return;
            
            const box = document.getElementById('chatBox');
            const btn = document.getElementById('sendBtn');
            
            btn.disabled = true;
            btn.textContent = '⏳ Envoi...';
            
            const time = new Date().toLocaleTimeString('fr-FR', {hour:'2-digit', minute:'2-digit'});
            box.innerHTML += '<div class="message user">' + msg + '<span class="time">' + time + '</span></div>';
            input.value = '';
            box.scrollTop = box.scrollHeight;
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'message=' + encodeURIComponent(msg)
                });
                const data = await response.json();
                
                const replyTime = new Date().toLocaleTimeString('fr-FR', {hour:'2-digit', minute:'2-digit'});
                let reply = data.response || 'Je n\\'ai pas compris ta question.';
                
                let sourcesHtml = '';
                if (data.sources && data.sources.length > 0) {
                    sourcesHtml = '<div class="sources"><strong>📖 Sources :</strong><br>';
                    data.sources.forEach(s => {
                        sourcesHtml += '• ' + (s.metadata?.filename || 'Document') + '<br>';
                    });
                    sourcesHtml += '</div>';
                }
                
                box.innerHTML += '<div class="message assistant">' + reply.replace(/\\n/g, '<br>') + sourcesHtml + '<span class="time">' + replyTime + '</span></div>';
            } catch (error) {
                box.innerHTML += '<div class="message assistant">🔌 Erreur: Impossible de contacter l\\'API.<br><br>📌 Lance l\\'API avec:<br><code>python backend/app/api/main.py</code></div>';
            }
            
            box.scrollTop = box.scrollHeight;
            btn.disabled = false;
            btn.textContent = '🚀 Envoyer';
        }
        
        function sendQuick(question) {
            document.getElementById('msgInput').value = question;
            sendMessage();
        }
    </script>
</body>
</html>
"""

# ========================================
# ESPACE ENSEIGNANT
# ========================================
PROF_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>NURU - Espace Enseignant</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
            padding: 30px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        .header h1 {
            font-size: 1.5rem;
            color: #2D3436;
        }
        .header h1 span.green { color: #00853F; }
        .header h1 span.yellow { color: #FDE100; }
        .header h1 span.red { color: #D63031; }
        .back-btn {
            padding: 6px 15px;
            border: 2px solid #E9ECEF;
            border-radius: 8px;
            background: white;
            color: #636E72;
            text-decoration: none;
            font-size: 0.85rem;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: #F8F9FA;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
        }
        .stat-card .num { font-size: 2rem; font-weight: 700; color: #00853F; }
        .stat-card .label { color: #636E72; font-size: 0.85rem; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th {
            text-align: left;
            padding: 10px 12px;
            background: #F8F9FA;
            font-weight: 600;
            border-bottom: 2px solid #E9ECEF;
        }
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #E9ECEF;
            color: #636E72;
        }
        .progress-bar {
            height: 6px;
            background: #E9ECEF;
            border-radius: 3px;
            overflow: hidden;
            width: 80px;
            display: inline-block;
            vertical-align: middle;
        }
        .progress-bar .fill {
            height: 100%;
            background: #00B894;
            border-radius: 3px;
        }
        .badge {
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
        }
        .badge.active { background: #00B89420; color: #00B894; }
        .badge.inactive { background: #D6303120; color: #D63031; }
        @media (max-width: 600px) { .stats { grid-template-columns: 1fr 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="green">N</span><span class="yellow">U</span><span class="red">R</span><span class="green">U</span> - Enseignant</h1>
            <a href="/" class="back-btn">🏠 Accueil</a>
        </div>
        <h2 style="margin:15px 0;">📊 Tableau de bord</h2>
        <div class="stats">
            <div class="stat-card"><div class="num">24</div><div class="label">👨‍🎓 Élèves</div></div>
            <div class="stat-card"><div class="num">87%</div><div class="label">📈 Réussite</div></div>
            <div class="stat-card"><div class="num">156</div><div class="label">📝 Exercices</div></div>
            <div class="stat-card"><div class="num">32</div><div class="label">📋 Quiz</div></div>
        </div>
        <h3>👨‍🎓 Liste des élèves</h3>
        <table>
            <tr><th>Élève</th><th>Classe</th><th>Progression</th><th>Statut</th></tr>
            <tr><td><strong>Fatou Diallo</strong></td><td>Terminale S1</td><td><span class="progress-bar"><div class="fill" style="width:85%"></div></span> 85%</td><td><span class="badge active">Actif</span></td></tr>
            <tr><td><strong>Mamadou Sow</strong></td><td>Terminale S1</td><td><span class="progress-bar"><div class="fill" style="width:62%"></div></span> 62%</td><td><span class="badge active">Actif</span></td></tr>
            <tr><td><strong>Aïssatou Diop</strong></td><td>Terminale S2</td><td><span class="progress-bar"><div class="fill" style="width:45%"></div></span> 45%</td><td><span class="badge inactive">Inactif</span></td></tr>
            <tr><td><strong>Ousmane Ndiaye</strong></td><td>Terminale S1</td><td><span class="progress-bar"><div class="fill" style="width:93%"></div></span> 93%</td><td><span class="badge active">Actif</span></td></tr>
            <tr><td><strong>Mariama Touré</strong></td><td>Terminale S2</td><td><span class="progress-bar"><div class="fill" style="width:78%"></div></span> 78%</td><td><span class="badge active">Actif</span></td></tr>
        </table>
        <div style="text-align:center; margin-top:30px; color:#B2BEC3; font-size:0.8rem;">🇸🇳 NURU - Tuteur IA pour l'Éducation au Sénégal</div>
    </div>
</body>
</html>
"""

# ========================================
# ROUTES FLASK
# ========================================

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/eleve')
def eleve():
    return render_template_string(ELEVE_HTML)

@app.route('/prof')
def prof():
    return render_template_string(PROF_HTML)

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/chat', methods=['POST'])
def chat():
    message = request.form.get('message', '')
    session_id = request.form.get('session_id') or None

    try:
        response = requests.post(
            f"{API_URL}/chat/",
            json={"message": message, "session_id": session_id},
            timeout=60
        )
        if response.status_code == 200:
            return jsonify(response.json())
    except Exception as e:
        print(f"⚠️ Erreur API: {e}")
    
    return jsonify({
        "response": f"🤖 **NURU (Mode hors-ligne)**\n\nMerci pour ta question : *\"{message}\"*\n\n📌 Pour utiliser NURU en mode complet :\n1. Lance l'API : `python -m backend.app.api.main`\n2. Assure-toi que Ollama tourne : `ollama serve`"
    })

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🚀 NURU - Interface Finale")
    print("=" * 80)
    print("📍 http://localhost:5000")
    print("📌 Espace Élève: http://localhost:5000/eleve")
    print("📌 Espace Enseignant: http://localhost:5000/prof")
    print("=" * 80 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
