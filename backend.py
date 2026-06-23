import os

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from supabase import Client, create_client

load_dotenv()

app = Flask(__name__)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app.secret_key = SECRET_KEY or "super-secret-chicago-key-12345"


def create_user(username: str, password: str):
    data = {
        "username": username,
        "password": password,
    }
    response = supabase.table("users").insert(data).execute()
    return response


def get_user_id(username: str):
    response = supabase.table("users").select("id").eq("username", username).execute()
    return response.data[0]["id"] if response.data else None


def get_user_info(user_id: str):
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None


def saved_contact(owner_id: str, username_id: str):
    data = {
        "owner_id": owner_id,
        "username_id": username_id,
    }
    response = supabase.table("saved_contacts").insert(data).execute()
    return response


def block(message: str, data, sender_id, sent_to_id):
    data = {
        "message": message,
        "data": data,
        "send_id": sender_id,
        "sent_to_id": sent_to_id,
    }
    return data


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    user = (
        supabase.table("users")
        .select("*")
        .eq("username", username)
        .eq("password", password)
        .execute()
    )
    if not user.data:
        return redirect(url_for("index"))
    session["username"] = username
    return redirect(url_for("home"))


@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return redirect(url_for("index"))
    response = create_user(username, password)
    session["username"] = username
    return redirect(url_for("home"))


@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
