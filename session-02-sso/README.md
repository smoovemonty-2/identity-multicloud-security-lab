# Session 2 — Microsoft Entra ID OIDC Flask Lab

This is a localhost-only training application, not production application code.

## Configure Entra
1. In **App registrations > lab-enterprise-portal > Authentication**, add a **Web** redirect URI exactly `http://localhost:3000/auth/redirect`.
2. Create a short-lived secret under **Certificates & secrets** and copy its **Value**, not its ID, into local `.env` only.
3. Under **API permissions**, keep only the required Microsoft Graph delegated `User.Read` permission for this exercise; no Graph application permissions.
4. Because Enterprise app **Assignment required?** is **Yes**, review the scope and grant admin consent for the minimal permission in your isolated test tenant. That consent does not by itself grant Taylor app access.
5. Keep Alex assigned and Taylor unassigned as configured in Session 1.

## Local setup

```bash
cd sso-app
python
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env`; fill in IDs and credential values. Create your Flask secret with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Run:

```bash
python app.py
```

Open `http://localhost:3000` in a private window. Sign in as Alex, verify the home page, then use `/me`. End the session and use a NEW private browser window to test Taylor; expected Entra failure: AADSTS50105. Review Entra **Sign-in logs** and document the error code and correlation ID if present.

## Security notes
- Do not commit `.env` or `.session_cache` or screenshots with tokens/identifiers.
- The local HTTP redirect URI is intended for `localhost` development only.
- Server-side disk sessions are for local development only; use a secure production-grade session backend and HTTPS in a real deployment.
- Local `/logout` only clears Flask's app session; a browser may still have an Entra SSO session. Use a fresh private window for each distinct identity.
- Never post access tokens, secret values, user passwords, or authentication codes to a chat, issue, or repository.
- The app intentionally does not implement business authorization; its SSO eligibility is controlled by Entra app assignments. Application authorization remains a separate concern.
