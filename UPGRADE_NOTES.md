# Upgrade notes

## Security hardening release (read SECURITY_AUDIT.md first)

**Before deploying**
1. Rotate every credential that was ever committed (database passwords, `SECRET_KEY`, API keys) and clean git history. Steps are in SECURITY_AUDIT.md section 1.
2. `SECRET_KEY` must now be **at least 32 characters** in production, or the API refuses to start. Run `python -m scripts.check_env` with your production variables first.
3. Render start command: add `--no-server-header`.
4. Supabase: run `python -m scripts.enable_rls --apply` once.

**What users will notice**
| Change | Effect |
|---|---|
| Tokens are bound to the password | Everyone is signed out once after the deploy. Changing or resetting a password signs out all other devices. |
| Argon2id passwords | Nothing to do. Old bcrypt hashes keep working and are upgraded on that user's next login. |
| Login lock-out | 5 wrong passwords from one IP for one account = 15 minute lock for that IP. (Configurable.) |
| CORS default | Only `FRONTEND_URL` may call the API from a browser. If the chat bubble breaks, set `CORS_ORIGINS` to the exact Streamlit URL. |
| `/docs` | Off in production. Set `ENABLE_DOCS=true` to bring it back. |
| Names, job text, email subjects | HTML and control characters are stripped on input. |
| Profile picture | `GET /users/me/picture` (own picture only). `profile_picture` (a server path) is no longer returned; `has_profile_picture` is. |

No database migration is required.

---

# Previous release notes

## Do these BEFORE deploying

1. **Rotate the leaked database passwords.** The Render Postgres URL (commits `0d8eb7f`, `83c7722`) and the Supabase URL (`a0c8204`, `c8a8031`) are still in git history. Reset the Supabase DB password (Project Settings → Database) and update `DATABASE_URL` on Render; delete the old Render database if unused.
2. **Set these environment variables on Render** (the app now refuses to start without the first two):
   - `SECRET_KEY` — long random value
   - `DATABASE_URL`
   - Email, one of: `RESEND_API_KEY` (+ `EMAIL_FROM`) **or** `ADMIN_EMAIL` + `ADMIN_EMAIL_PASSWORD`. Render's free tier is believed to block SMTP ports, so Resend (HTTPS) is the safer choice. Admin 2FA codes are emailed, so without working email admins cannot sign in.
   - Chat: `ANTHROPIC_API_KEY` and/or `GEMINI_API_KEY`
3. Confirm your admin account exists with role `admin` (it does if you could use the admin panel before). If not: `python -m scripts.manage_admin promote you@example.com`.
4. Streamlit secret `API_URL` must be your Render URL (the chat bubble now uses it instead of a hardcoded address).

## Behaviour changes

| Change | Effect |
|---|---|
| Admin password login removed | Admins must use the **Admin 2FA** page; the normal login page now points them there |
| Signup never creates admins | Use `scripts/manage_admin.py` |
| Reset tokens hashed | Reset links issued before the deploy stop working (they only last 1 hour) |
| `sex` no longer collected | Column kept (no migration); old clients may still send it, it is ignored |
| Duplicate resumes | Blocked per user only; reuse on another account is flagged, not blocked |
| Jobs with applications | `DELETE /jobs/{id}` returns 409 instead of a 500 |
| Scores | Text similarity is rescaled (`SIMILARITY_FULL_MATCH` in `ai_engine.py`), so overall scores are higher than before; ranking order is unchanged. Old applications keep their old scores until you call `POST /admin/jobs/{id}/rescore` |
| CORS | Still `*` by default (the chat bubble calls the API from the browser) but no credentials; restrict with `CORS_ORIGINS` |

No database migration is required.

## If admin login breaks after deploy
Set `OTP_DELIVERY=log` temporarily: the code appears in the Render logs. Fix email, then remove it.

## Optional: scrub git history
After rotating passwords, history cleanup is optional hygiene:
`pip install git-filter-repo` → `git filter-repo --replace-text secrets.txt` → `git push --force`. Forks keep their copies, which is why rotation is the real fix.
