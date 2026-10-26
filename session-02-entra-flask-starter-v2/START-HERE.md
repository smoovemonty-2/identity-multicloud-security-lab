# Session 2 — Entra Flask SSO Starter (macOS/Windows friendly)

Open `sso-app/README.md` for the full instructions.

The original `.env.example` and `.gitignore` files are included, but Finder on macOS hides filenames beginning with a dot. Press **Command + Shift + .** to toggle hidden files.

For convenience, this archive also includes two visible copies:
- `sso-app/env-template.txt` — copy to a new file named `.env`, then replace every placeholder locally. Never commit or share your `.env` file.
- `sso-app/gitignore-template.txt` — same content as the real `.gitignore` (which is already present and does not need recreating).

A quick macOS/Linux terminal command to create `.env` from the included template:

```sh
cd sso-app
cp env-template.txt .env
```

Keep `sso-app/.gitignore` in place, especially before initializing a Git repository.
