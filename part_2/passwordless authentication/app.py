from flask import Flask, render_template, request, redirect, url_for, flash
import json, os, random
from utils import login_user, retrieve_user, database, cookies, send_otp, tokens
from flask_mail import Mail
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = "A very secure secret"


# configure flask mail settings
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = os.getenv("EMAIL_ADDRESS")
app.config["MAIL_PASSWORD"] = os.getenv("EMAIL_APP_PASSWORD")
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

# initialize mail object
mail = Mail(app)


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
            page="Login Form",
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

    email = request.form.get("email")
    resp = send_otp(mail, email)
    return resp


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template(
            "login.html",
            page="Registration Form",
            action="Register",
            alt="Already have an account",
            alt_text="Login",
            alt_route="/login",
        )

    email = request.form.get("email")
    resp = send_otp(mail, email)
    return resp


@app.route("/verify_otp", methods=["POST", "GET"])
def verify_otp():
    if request.method == "GET":
        return render_template(
            "login.html",
            page="Verify OTP",
            action="Verify",
            alt="Don't have an account",
            alt_text="Register",
            alt_route="/register",
        )
    otp = request.form.get("otp")

    if not otp:
        flash("OTP not provided")
        return redirect(url_for("verify_otp"))

    email = tokens.get(otp)

    if not email:
        flash("Invalid OTP provided")
        return redirect(url_for("verify_otp"))

    resp, id = login_user()
    cookies[id] = email

    if not database.get(email):
        database[email] = {"balance": 400}
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
