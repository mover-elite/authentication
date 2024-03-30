from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    make_response,
)
from utils import login_user, retrieve_user, database, decode_token
from dotenv import load_dotenv
import json, requests, secrets
from config import odic_provider, client_id


load_dotenv()
app = Flask(__name__)
app.secret_key = "A very secure secret"

oidc_provider_configuration = {}


@app.route("/")
def home():
    user_email, user = retrieve_user()
    if not user:
        return redirect(url_for("login"))
    return render_template("index.html", user=user, email=user_email)


@app.route("/login", methods=["POST", "GET"])
def login():
    authorizationEndpoint = oidc_provider_configuration["authorization_endpoint"]
    response_type = "id_token"
    scope = "openid email"

    redirect_uri = "http://localhost:5001/callback"
    response_mode = "query"
    nonce = secrets.token_urlsafe()
    print(authorizationEndpoint)
    response = make_response(
        redirect(
            f"""{authorizationEndpoint}?response_mode={response_mode}&response_type={response_type}&scope={scope}&client_id={client_id}&redirect_uri={redirect_uri}&nonce={nonce}"""
        )
    )
    response.set_cookie("auth-nonce", nonce)
    return response


@app.route("/callback", methods=["POST", "GET"])
def handle_callback():
    if request.method == "POST":
        print("Called")
        token = request.form.get("id_token")
    else:
        code = request.args.get("code")
        data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": code,
            "redirect_uri": "http://localhost:5001/callback",
        }

        res = requests.post(oidc_provider_configuration["token_endpoint"], data=data)
        if res.status_code != 200:
            return "Unable to login"
        token = res.json()["id_token"]

    data = decode_token(token, oidc_provider_configuration["jwks_uri"])
    resp = login_user(data["email"])
    resp.delete_cookie("auth-nonce")
    return resp


@app.route("/transact", methods=["POST"])
def send_money():
    data = json.loads(request.data)
    action = data["action"]

    email, user = retrieve_user()

    if not user:
        return {"status": "error", "message": "user not found"}

    user_bal = user["balance"]
    new_balance = user_bal - 4 if action == "send" else user_bal + 10

    if new_balance < 0:
        return {"Insufficient Balance please Refund"}

    database[email]["balance"] = new_balance
    return {"new_balance": new_balance}


if __name__ == "__main__":
    try:
        res = requests.get(f"{odic_provider}/.well-known/openid-configuration")
        oidc_provider_configuration = res.json()
        app.run(debug=True, port=5001)
    except Exception as e:
        print(e)
        print("Couldn't connect to the OpenID provider for configuration")
