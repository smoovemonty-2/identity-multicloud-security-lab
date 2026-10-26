"""Local Entra ID SSO lab: Flask + MSAL authorization-code flow.

For local development only; review and harden before any deployment.
"""
import os
from datetime import timedelta

import msal
import requests
from cachelib.file import FileSystemCache
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, redirect, render_template_string, request, session, url_for
from flask_session import Session

load_dotenv()
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
TENANT_ID = os.environ["TENANT_ID"]
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:3000/auth/redirect")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read"]  # Delegated Microsoft Graph permission; no application permissions.

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ["FLASK_SECRET_KEY"],
    SESSION_TYPE="cachelib",
    SESSION_CACHELIB=FileSystemCache(cache_dir=".session_cache", threshold=100),
    SESSION_PERMANENT=False,
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # Localhost HTTP ONLY. True behind HTTPS in deployment.
)
Session(app)


def identity_client():
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )


HOME = """<!doctype html>
<title>Enterprise Portal SSO Lab</title>
<h1>Enterprise Portal SSO Lab</h1>
{% if user %}
  <p>Signed in: {{ user.name }}</p>
  <p><a href='{{ url_for("profile") }}'>Read my Microsoft Graph profile</a></p>
  <p><a href='{{ url_for("logout") }}'>End local session</a></p>
{% else %}
  <p><a href='{{ url_for("login") }}'>Sign in with Entra ID</a></p>
{% endif %}
"""


@app.get("/")
def index():
    return render_template_string(HOME, user=session.get("user"))


@app.get("/login")
def login():
    flow = identity_client().initiate_auth_code_flow(
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        prompt="select_account"
    )
    if "auth_uri" not in flow:
        abort(500, "Unable to start sign-in")
    session["auth_flow"] = flow
    return redirect(flow["auth_uri"])


@app.get("/auth/redirect")
def auth_redirect():
    flow = session.pop("auth_flow", None)
    if not flow:
        abort(400, "No sign-in request found. Start at /login.")
    try:
        result = identity_client().acquire_token_by_auth_code_flow(
            flow, request.args.to_dict()
        )
    except ValueError:
        abort(400, "Sign-in state validation failed. Start again.")
    if "access_token" not in result:
        # Do not print tokens, codes, client secrets, or sensitive details.
        abort(401, "Sign-in was not completed. Check Entra sign-in logs.")
    claims = result.get("id_token_claims", {})
    session["user"] = {"name": claims.get("name", "User")}
    # Local server-side session only; never send access tokens to the browser page.
    session["access_token"] = result["access_token"]
    return redirect(url_for("index"))


@app.get("/me")
def profile():
    token = session.get("access_token")
    if not token:
        return redirect(url_for("login"))
    try:
        response = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
    except requests.RequestException:
        abort(502, "Microsoft Graph request failed")
    if not response.ok:
        abort(502, f"Microsoft Graph returned HTTP {response.status_code}")
    # Lab account only. Treat response as sensitive and do not publish raw output.
    return jsonify(response.json())


@app.get("/logout")
def logout():
    session.clear()  # Ends Flask session, not necessarily the Entra browser SSO session.
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="localhost", port=3000, debug=False)
