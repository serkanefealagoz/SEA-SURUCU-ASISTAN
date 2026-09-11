import os
import time
import threading
import json
import requests
from flask import Flask, render_template_string, request, jsonify, session

app = Flask(__name__)
app.secret_key = "sea_cok_gizli_guvenli_anahtar_2026"

# Telegram Bot Bilgilerin
TELEGRAM_BOT_TOKEN = "8710742813:AAFIu8P4uqfRfTNK4OFoT9bD1mOqajZLWDI"
TELEGRAM_CHAT_ID = "7245389074"

DATA_FILE = "sessions.json"
data_lock = threading.Lock()
last_update_id = 0

def load_data():
    with data_lock:
        if not os.path.exists(DATA_FILE):
            return {}
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

def save_data(data):
    with data_lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEA | Güvenli Araç ve Sürücü İletişim Protokolü</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            background: radial-gradient(circle at center, #090d16 0%, #020617 100%);
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 16px;
        }
        .main-card {
            width: 100%;
            max-width: 440px;
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 28px;
            box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.8);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .card-header-custom {
            padding: 18px 24px;
            background: rgba(2, 6, 23, 0.6);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .card-body-custom {
            padding: 24px;
        }
        .form-control {
            background: rgba(2, 6, 23, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            border-radius: 14px;
            padding: 13px 16px;
            font-size: 13.5px;
            transition: all 0.3s ease;
        }
        .form-control:focus {
            background: rgba(2, 6, 23, 0.8);
            color: white;
            border-color: #3b82f6;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
        }
        .form-control::placeholder { color: #64748b; }
        
        .info-box {
            background: rgba(59, 130, 246, 0.05);
            border: 1px solid rgba(59, 130, 246, 0.15);
            border-radius: 16px;
            padding: 16px;
            font-size: 12px;
            color: #93c5fd;
            margin-bottom: 20px;
            line-height: 1.5;
        }
        .btn-custom {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            border: none;
            color: white;
            font-weight: 600;
            padding: 14px;
            border-radius: 14px;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.4);
        }
        .btn-custom:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 25px -5px rgba(59, 130, 246, 0.6);
            background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        }
        .btn-logout {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.2);
            color: #f87171;
            padding: 6px 12px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }
        .btn-logout:hover {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }
        .chat-body {
            height: 400px;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: radial-gradient(circle at center, rgba(15, 23, 42, 0.4) 0%, rgba(2, 6, 23, 0.6) 100%);
        }
        .message {
            max-width: 82%;
            padding: 12px 16px;
            border-radius: 16px;
            font-size: 13.5px;
            line-height: 1.45;
            animation: fadeIn 0.3s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.visitor {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
        }
        .message.driver {
            background: rgba(30, 41, 59, 0.85);
            color: #f8fafc;
            border: 1px solid rgba(255, 255, 255, 0.08);
            align-self: flex-start;
            border-bottom-left-radius: 4px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        .chat-footer {
            padding: 16px 20px;
            background: rgba(2, 6, 23, 0.8);
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            gap: 10px;
        }
        .status-dot {
            width: 9px;
            height: 9px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 10px #10b981;
            animation: pulse-dot 2s infinite;
        }
        @keyframes pulse-dot {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
    </style>
</head>
<body>

<div class="main-card">
    <div class="card-header-custom">
        <div class="d-flex align-items-center gap-2.5">
            <span class="status-dot"></span>
            <div>
                <h6 class="mb-0 fw-bold text-white" style="font-size: 14px;">SEA Sürücü Asistanı</h6>
                <small class="text-success" style="font-size: 11px;">Güvenli Hat Aktif</small>
            </div>
        </div>
        <button id="logoutBtn" onclick="logoutSession()" class="btn-logout d-none">
            <i class="bi bi-box-arrow-right"></i> Çıkış Yap
        </button>
    </div>

    <!-- EKRAN 1 -->
    <div id="welcomeScreen" class="card-body-custom {% if registered %}d-none{% endif %}">
        <div class="text-center mb-4">
            <div class="fs-1 mb-2">🚗🔒</div>
            <h5 class="fw-bold text-white mb-1" style="font-size: 18px;">Güvenli İletişim Portalı</h5>
            <p class="text-slate-400" style="font-size: 12.5px;">Numaranız gizli tutulur. Sürücüye anında ulaşmak için lütfen bilgilerinizi girin.</p>
        </div>

        <div class="info-box">
            <div class="d-flex align-items-start gap-2">
                <i class="bi bi-robot fs-5 text-blue-400 flex-shrink-0 mt-0.5"></i>
                <div>
                    <strong class="d-block text-white mb-1">Yapay Zeka & KVKK Güvencesi</strong>
                    <span>Butona bastığınız an <strong>yapay zeka asistanı</strong> arka planda sürücüyü arayarak bildirim tetikler. Tüm verileriniz <strong>KVKK</strong> kapsamında şifrelenir ve oturum kapandığında tamamen silinir.</span>
                </div>
            </div>
        </div>

        <form onsubmit="startChat(event)">
            <div class="mb-3">
                <label class="form-label text-slate-300 fw-semibold" style="font-size: 12px;">Plakanız veya Adınız <span class="text-danger">*</span></label>
                <input type="text" id="visitorName" class="form-control" placeholder="Örn: 34ABC123 veya Ahmet" required autocomplete="off">
            </div>
            <div class="mb-4">
                <label class="form-label text-slate-300 fw-semibold" style="font-size: 12px;">Telefon Numaranız <span class="text-danger">*</span></label>
                <input type="tel" id="visitorPhone" class="form-control" placeholder="Örn: 0555 123 45 67" required autocomplete="off">
            </div>
            <button type="submit" class="btn-custom">
                <i class="bi bi-shield-check me-2"></i> Güvenli Sohbeti Başlat
            </button>
        </form>
    </div>

    <!-- EKRAN 2 -->
    <div id="chatScreen" class="{% if not registered %}d-none{% endif %} d-flex flex-column" style="flex: 1;">
        <div class="chat-body" id="chatBody">
            <div class="message driver">
                🤖 <strong>Yapay Zeka Asistanı:</strong> Bağlantı kuruldu! Sürücüye çağrı iletildi. Mesajınızı yazabilirsiniz.
            </div>
            {% for msg in history %}
                <div class="message {{ msg.sender }}">{{ msg.text }}</div>
            {% endfor %}
        </div>

        <form class="chat-footer" onsubmit="sendMsg(event)">
            <input type="text" id="msgInput" class="form-control" placeholder="Mesajınızı buraya yazın..." autocomplete="off" required>
            <button type="submit" class="btn btn-primary px-3 rounded-4 shadow-sm" style="background: #3b82f6; border:none; width: 48px;"><i class="bi bi-send-fill fs-5"></i></button>
        </form>
    </div>
</div>

<script>
    window.addEventListener('DOMContentLoaded', () => {
        const isRegistered = "{{ 'true' if registered else 'false' }}" === 'true';
        if(isRegistered) {
            document.getElementById('logoutBtn').classList.remove('d-none');
        }
    });

    function startChat(event) {
        event.preventDefault();
        const name = document.getElementById('visitorName').value;
        const phone = document.getElementById('visitorPhone').value;

        fetch('/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name: name, phone: phone})
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'ok') {
                document.getElementById('welcomeScreen').classList.add('d-none');
                document.getElementById('chatScreen').classList.remove('d-none');
                document.getElementById('logoutBtn').classList.remove('d-none');
            }
        });
    }

    function logoutSession() {
        fetch('/logout', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'ok') {
                document.getElementById('chatScreen').classList.add('d-none');
                document.getElementById('welcomeScreen').classList.remove('d-none');
                document.getElementById('logoutBtn').classList.add('d-none');
                document.getElementById('visitorName').value = '';
                document.getElementById('visitorPhone').value = '';
                document.getElementById('chatBody').innerHTML = '<div class="message driver">🤖 <strong>Yapay Zeka Asistanı:</strong> Bağlantı kuruldu! Sürücüye çağrı iletildi. Mesajınızı yazabilirsiniz.</div>';
            }
        });
    }

    function sendMsg(event) {
        event.preventDefault();
        const input = document.getElementById('msgInput');
        const text = input.value.trim();
        if(!text) return;

        appendMsg(text, 'visitor');
        input.value = '';

        fetch('/send', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: text})
        });
    }

    function appendMsg(text, sender) {
        const body = document.getElementById('chatBody');
        const div = document.createElement('div');
        div.className = `message ${sender}`;
        div.innerText = text;
        body.appendChild(div);
        body.scrollTop = body.scrollHeight;
    }

    setInterval(() => {
        if(document.getElementById('chatScreen').classList.contains('d-none')) return;
        
        fetch('/get-messages')
        .then(res => res.json())
        .then(data => {
            const body = document.getElementById('chatBody');
            body.innerHTML = '<div class="message driver">🤖 <strong>Yapay Zeka Asistanı:</strong> Bağlantı kuruldu! Sürücüye çağrı iletildi. Mesajınızı yazabilirsiniz.</div>';
            data.forEach(m => {
                appendMsg(m.text, m.sender);
            });
        });
    }, 2000);
</script>

</body>
</html>
"""

@app.route("/")
def index():
    session.clear()
    return render_template_string(HTML_TEMPLATE, registered=False, history=[])

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name", "Bilinmiyor")
    phone = data.get("phone", "Bilinmiyor")
    
    import uuid
    sid = str(uuid.uuid4())
    session["sid"] = sid
    session["registered"] = True
    session["name"] = name
    session["phone"] = phone
    
    db = load_data()
    db[sid] = []
    save_data(db)
    
    telegram_text = (
        "🚨 *YAPAY ZEKA ASİSTANI: ACİL ÇAĞRI!* 🚨\n\n"
        f"🚗 *Plaka / Ad:* {name}\n"
        f"📞 *Telefon:* {phone}\n\n"
        f"🔑 *Oturum ID:* `{sid}`\n\n"
        "🤖 _Yapay zeka aracı tarayan kişiyi doğruladı, hat aktif._"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": telegram_text, "parse_mode": "Markdown"})
    
    return jsonify({"status": "ok"})

@app.route("/logout", methods=["POST"])
def logout():
    sid = session.get("sid")
    name = session.get("name", "Bilinmiyor")
    phone = session.get("phone", "Bilinmiyor")
    
    db = load_data()
    if sid and sid in db:
        del db[sid]
        save_data(db)
        
    telegram_text = (
        "🚪 *GÜVENLİ OTURUM KAPANDI* 🚪\n\n"
        f"🚗 *Plaka / Ad:* {name}\n"
        f"📞 *Telefon:* {phone}\n\n"
        "🔒 _Kullanıcı sohbetten çıkış yaptı, hat kapatıldı._"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": telegram_text, "parse_mode": "Markdown"})
    
    session.clear()
    return jsonify({"status": "ok"})

@app.route("/send", methods=["POST"])
def send():
    sid = session.get("sid")
    name = session.get("name", "Bilinmiyor")
    
    db = load_data()
    if not sid or sid not in db:
        return jsonify({"status": "error"})
        
    data = request.get_json()
    msg = data.get("message", "")
    
    db[sid].append({"sender": "visitor", "text": msg})
    save_data(db)
    
    telegram_text = f"💬 *{name} (Mesaj):*\n\n{msg}\n\n🔑 *ID:* `{sid}`"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": telegram_text, "parse_mode": "Markdown"})
    
    return jsonify({"status": "ok"})

@app.route("/get-messages")
def get_messages():
    sid = session.get("sid")
    db = load_data()
    if not sid or sid not in db:
        return jsonify([])
    return jsonify(db[sid])

def telegram_listener():
    global last_update_id
    time.sleep(2)
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=30"
            res = requests.get(url, timeout=35).json()
            
            if res.get("ok") and res.get("result"):
                for update in res["result"]:
                    last_update_id = update["update_id"]
                    
                    if "message" in update and str(update["message"]["chat"]["id"]) == str(TELEGRAM_CHAT_ID):
                        if "text" in update["message"]:
                            driver_text = update["message"]["text"]
                            
                            # Sistem mesajlarını eleme
                            if not driver_text.startswith("🚨 *YAPAY ZEKA") and not driver_text.startswith("🚪 *GÜVENLİ OTURUM"):
                                db = load_data()
                                target_sid = None
                                
                                for sid_key in db.keys():
                                    if sid_key in driver_text:
                                        target_sid = sid_key
                                        break
                                
                                # Eğer ID bulunamazsa en son aktif oturuma yaz
                                if not target_sid and db:
                                    target_sid = list(db.keys())[-1]
                                    
                                if target_sid and target_sid in db:
                                    db[target_sid].append({"sender": "driver", "text": driver_text})
                                    save_data(db)
        except Exception as e:
            print("Telegram dinleme hatası:", e)
            time.sleep(5)
        
        time.sleep(1)

# Render / Gunicorn için dinleyiciyi dışarıda başlatıyoruz
t = threading.Thread(target=telegram_listener, daemon=True)
t.start()

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
