from flask import make_response, redirect, url_for, flash, session
from typing import Dict
import jwt
from jwt import PyJWKClient
from config import client_id
import random, string, os


letters = list(string.ascii_letters)

database: Dict[str, Dict[str, int]] = {}
tokens: Dict[str, str] = {}
database["aaa@gmail.com"] = {"balance": 400}


def login_user(user):
    session["current-user"] = user
    if not database.get(user):
        database[user] = {"balance": 400}
    resp = make_response(redirect(url_for("home")))
    return resp


def retrieve_user():
    current_user = session.get("current-user")
    if not current_user:
        return None, None
    user_details = database.get(current_user, {})
    return current_user, user_details


def decode_token(token, jwks_uri):
    jwks_client = PyJWKClient(jwks_uri)
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    data = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=client_id,
        options={"verify_exp": True},
    )
    print(data)
    return data
