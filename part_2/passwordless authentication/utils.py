from flask import make_response, redirect, url_for, flash
from typing import Dict
import random, string, os
from flask_mail import Mail, Message

email_address = os.getenv("EMAIL_ADDRESS")
letters = list(string.ascii_letters)

database: Dict[str, Dict[str, int]] = {}
tokens: Dict[str, str] = {}
database["aaa@gmail.com"] = {"balance": 400}
cookies: Dict[str, str] = {}


def login_user():
    id = "".join(random.sample(letters, 10))
    resp = make_response(redirect(url_for("home")))
    resp.set_cookie("auth_cookie", id)
    return resp, id


def retrieve_user(cookie):
    user_email = cookies.get(cookie, "")
    user_details = database.get(user_email, {})
    return user_email, user_details


def send_otp(mail, email):
    token = "".join(random.sample(letters, 5))
    msg = Message("Login Token", sender=email_address, recipients=[email])
    msg.body = f"Your login token is {token}"
    print(msg.body)

    tokens[token] = email
    # mail.send(msg)
    resp = make_response(redirect(url_for("verify_otp")))
    return resp
