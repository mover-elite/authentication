from flask import Flask, render_template, request, redirect, url_for, make_response
from cryptography.fernet import Fernet
import random
import string


app = Flask(__name__)

letters = list(string.ascii_letters)
names = {}  # type: ignore

encryption_key = "VlD8h2tEiJkQpKKnDNKnu8ya2fpIBMOo5oc7JKNasvk=".encode()
f = Fernet(encryption_key)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/set_cookie", methods=["POST"])
def get_cookies():
    name = request.form.get("name")
    if not name:
        return redirect(url_for("home"))
    id = "".join(random.sample(letters, 10))
    names[id] = name
    resp = make_response(render_template("index.html"))
    resp.set_cookie("name_cookie", id)
    return resp


@app.route("/token")
def token_home():
    return render_template("token.html")


@app.route("/get_auth_token", methods=["POST"])
def get_auth_token():
    name = request.form.get("name")

    if not name:
        return redirect(url_for("token_home"))
    print(name)
    encrypted = f.encrypt(name.encode())
    return {"token": encrypted.decode()}


@app.route("/retrieve_user")
def retrieve_user():
    auth_header = request.headers.get("Authorization")
    if auth_header:
        auth_token = auth_header.split(" ")[1]
        name = f.decrypt(auth_token.encode())
        print(name)
        return {"user": name.decode()}


if __name__ == "__main__":
    app.run(debug=True)
