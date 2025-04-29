from flask import Flask, render_template, request, redirect, session, abort
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import os, threading, time, requests, datetime

# .env 로드
load_dotenv()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)


app.secret_key = SECRET_KEY
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Self-ping 스레드
def keep_alive():
    while True:
        try:
            requests.get("https://giga-camp-app.onrender.com")
        except:
            pass
        time.sleep(14 * 60)

threading.Thread(target=keep_alive, daemon=True).start()

@app.before_request
def log_request():
    # 이제 request.remote_addr가 실제 클라이언트 IP를 반환합니다
    ip = request.remote_addr
    path = request.path
    ua = request.user_agent.string
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log = f"[{timestamp}] IP: {ip} | Path: {path} | UA: {ua}\n"
    with open("access.log", "a", encoding="utf-8") as f:
        f.write(log)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/project/<project_id>")
def project_detail(project_id):
    try:
        return render_template(f"project_{project_id}.html")
    except:
        return "페이지를 찾을 수 없습니다 😢", 404

# 로그인
@app.route("/logen", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect("/admin/logs")
        else:
            return "❌ 로그인 실패!", 401
    return render_template("login.html")

# 로그아웃
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# 관리자 로그 뷰
@app.route("/admin/logs", methods=["GET", "POST"])
def view_logs():
    if not session.get("logged_in"):
        return redirect("/logen")

    # 오늘 날짜 기본값
    selected_date = datetime.datetime.now().strftime("%Y-%m-%d")
    if request.method == "POST":
        selected_date = request.form.get("date", selected_date)

    selected_prefix = f"[{selected_date}"

    try:
        with open("access.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            logs = [line for line in lines if line.startswith(selected_prefix)]

        # 날짜 리스트 생성: 고유 날짜들만 추출
        available_dates = sorted({line[1:11] for line in lines if line.startswith("[")}, reverse=True)

    except FileNotFoundError:
        logs = ["(아직 로그 없음)"]
        available_dates = []

    return render_template("logs.html", logs=logs, available_dates=available_dates, selected_date=selected_date)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
