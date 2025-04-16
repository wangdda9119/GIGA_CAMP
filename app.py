from flask import Flask, render_template
import threading
import time
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/project/<project_id>')
def project_detail(project_id):
    try:
        print(f"project_{project_id}.html")
        return render_template(f'project_{project_id}.html')
    except:
        return "페이지를 찾을 수 없습니다 😢", 404

# 🔁 Render 슬립 방지를 위한 self-ping 함수
def keep_render_awake():
    while True:
        try:
            res = requests.get("https://giga-camp-app.onrender.com/")  # ← 여기에 네 실제 Render 주소 입력!
            #print(f"[PING] Status: {res.status_code}")
        except Exception as e:
            print(f"[PING ERROR] {e}")
        time.sleep(14 * 60)  # 14분마다 ping

# 🔧 Flask 서버 실행 전에 self-ping 스레드 실행
if __name__ == "__main__":
    threading.Thread(target=keep_render_awake, daemon=True).start()
    app.run(debug=True, host='0.0.0.0')
