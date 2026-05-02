from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from chatbot import get_bot_response
from database import init_db, save_chat, get_all_chats, seed_faq
import os

app = Flask(__name__)

# IMPORTANT: needed for session stability on Render
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_key_123")

# initialize database
init_db()
seed_faq()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- CHAT ----------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"reply": "Invalid request"}), 400

        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please type something."})

        if "context" not in session:
            session["context"] = {}

        bot_response = get_bot_response(user_message, session["context"])

        reply = bot_response["reply"]
        session["context"] = bot_response["context"]

        save_chat(user_message, reply)

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "Server error. Please try again."}), 500


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "1234":
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("login"))


# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    return render_template("admin.html")


# ---------------- GET CHATS ----------------
@app.route("/get_chats")
def get_chats():
    if not session.get("admin_logged_in"):
        return jsonify([])

    chats = get_all_chats()
    return jsonify(chats)


# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)