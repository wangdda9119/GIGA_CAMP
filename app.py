# app.py
from flask import Flask, render_template

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


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')  # ← 요거 중요!!
