from flask import make_response, redirect, url_for, flash
from typing import Dict
import random
import string

letters = list(string.ascii_letters)

database: Dict[str, Dict[str, int | str]] = {}
database["aaa@gmail.com"] = {"password": "asdf", "balance": 400}
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
