from flask import Flask, render_template, request, redirect, url_for, flash
import json
from utils import login_user, retrieve_user, database, cookies

app = Flask(__name__)
app.secret_key = "A very secure secret"


@app.route("/")
def home():
    auth_cookie = request.cookies.get("auth_cookie")
    _, user = retrieve_user(auth_cookie)

    if not user:
        flash("User not found")
        return redirect(url_for("login"))

    return render_template("index.html", user=user)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template(
            "login.html",
            page="Login",
            action="Login",
            alt="Don't have an account",
            alt_text="Register",
            alt_route="/register",
        )

    email = request.form.get("email")
    user_exists = database.get(email, {})
    if not user_exists:
        flash("User Account does not exist")
        return redirect(url_for("login"))

    user_password = user_exists["password"]
    password = request.form.get("password")

    if user_password != password:
        flash("Incorrect password ")
        return redirect(url_for("login"))
    resp, id = login_user()
    cookies[id] = email
    return resp


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template(
            "login.html",
            page="Registration",
            action="Register",
            alt="Already have an account",
            alt_text="Login",
            alt_route="/login",
        )

    email = request.form.get("email")
    password = request.form.get("password")
    database[email] = {"password": password, "balance": 400}
    resp, id = login_user()
    cookies[id] = email
    return resp


@app.route("/transact", methods=["POST"])
def send_money():
    data = json.loads(request.data)
    action = data["action"]

    auth_token = request.cookies.get("auth_cookie")
    email, user = retrieve_user(auth_token)

    if not user:
        return {"status": "error", "message": "user not found"}

    user_bal = user["balance"]
    new_balance = user_bal - 4 if action == "send" else user_bal + 10

    if new_balance < 0:
        return {"Insufficient Balance please Refund"}

    database[email]["balance"] = new_balance
    return {"new_balance": new_balance}


if __name__ == "__main__":
    app.run(debug=True)
