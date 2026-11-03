# Security audit and hardening report

Audit date: 2026-11-01. Scope: the whole repository (FastAPI backend, Streamlit frontend, CI, config, git history).

Tools used: `pip-audit` (known vulnerabilities), `bandit` (static analysis), `pyflakes`/`vulture` (unused code),
a custom secret scanner over the current files **and every past commit**, a real PostgreSQL 16 for the database
checks, and Streamlit's headless test harness driving every page against a live backend.

Result after the fixes: 116 backend tests pass, `pip-audit` reports 0 vulnerabilities (backend and frontend),
`bandit` reports 0 issues, the secret scan of current files is clean, 22/22 end-to-end UI checks pass.

---

## 1. Things only YOU can do (code cannot fix these)

| # | Action | Why |
|---|--------|-----|
| 1 | **Rotate every credential that ever appeared in git history.** Supabase database password (both the direct and the pooler URL), the Render Postgres password, `SECRET_KEY`, and any API key (Resend, Anthropic, Gemini). | The history scan found live-looking Supabase and Render database URLs, a hard-coded `SECRET_KEY`, and an `API_KEY=` line in old commits. Deleting a file does not remove it from history; anyone who cloned the repo (or any fork) still has them. |
| 2 | **Remove the committed files from history**, then force-push (steps below). | `backend/.env`, `backend/database.db` (user data) and a personal resume PDF (`backend/uploads/...ALLAN KAMAU.pdf`) were committed once. |
| 3 | Run `python -m scripts.enable_rls --apply` against the Supabase database. | Supabase exposes the `public` schema through a REST API that works with the project's *public* anon key. Tables without row-level security can be read through it, including `users`. The backend is unaffected because it connects as the table owner. |
| 4 | Add `--no-server-header` to the Render start command. | Stops the server announcing `server: uvicorn`. |
| 5 | Run `python -m scripts.check_env` with your production variables before deploying. | Catches a weak key, wildcard CORS, docs enabled, etc. It never prints a secret. |

History clean-up (do this *after* rotating, and keep a backup first):

```bash
git clone --mirror <repo-url> hiring-backup.git          # backup
pip install git-filter-repo
git filter-repo --invert-paths \
  --path backend/.env --path backend/database.db --path backend/uploads
# Optional: replace hard-coded strings. Put one  literal==>REMOVED  per line in replace.txt
git filter-repo --replace-text replace.txt
git remote add origin <repo-url>
git push --force --all && git push --force --tags
```

Forks and old clones keep their copies, which is why rotation (step 1) is what actually protects you.

---

## 2. What was found and what was done

Legend: **Fixed** = changed in code, covered by a test. **Manual** = needs you (section 1).

| Requested item | Finding | Result |
|---|---|---|
| **Remove unused packages** | `python-jose` (and its `ecdsa`, `rsa`, `pyasn1` chain) had two known vulnerabilities and is poorly maintained; `passlib` is unmaintained and forced a pin on `bcrypt==4.0.1`; `uvicorn[standard]` pulled in 5 unused packages; `python-dotenv` was listed twice (pydantic-settings already brings it). Unused imports in 5 files. | **Fixed.** Replaced `python-jose` with `PyJWT`, `passlib` with `argon2-cffi` + `bcrypt`, `uvicorn[standard]` with `uvicorn`, dropped the duplicate. Dead code removed (`require_recruiter_or_admin`, unused imports, debug output). |
| **Check for secrets** | Current files are clean. History is not (see section 1). `.gitignore` lacked `*.pem`, `*.key`, `secrets.toml`, uploads in some paths. | **Fixed + Manual.** Added `scripts/scan_secrets.py` (runs in CI and in the test suite, `--history` for past commits). Expanded `.gitignore`. Rotation is manual. |
| **Add rate limiting** | Most routes were limited, but: `/chat` had only a *global* daily cap (one person could use it all up), profile and admin write routes had no stricter limit, and there was no per-account brute-force lock. | **Fixed.** Per-route limits on every write route; login lock-out per (email + IP) and per email; per-visitor daily chat allowance; global default of 120/min on everything else. |
| **Check user access** | Authorization was correct (roles read from the database, ownership checked on resumes/applications). One gap: a token stayed valid after the password changed. | **Fixed.** Tokens are bound to the password they were issued under (`pwv` claim), so a reset or change signs out every old session. A test walks **every route** and fails if one that should be protected answers an anonymous caller, and checks every admin route rejects a candidate. |
| **Hash passwords properly** | bcrypt silently ignored everything after 72 bytes of the password. | **Fixed.** New hashes are **Argon2id**. Existing bcrypt hashes still work and are upgraded automatically the next time that user logs in. Added a common-password deny list. |
| **Hide my API keys** | Keys were only in environment variables (good) but were plain strings, so they would show up in any `repr(settings)`, debug print or error report. They never reach the browser (the chat widget calls *your* backend). | **Fixed.** All secrets (`SECRET_KEY`, `DATABASE_URL`, email password, Resend/Anthropic/Gemini keys) are `SecretStr`: they print as `**********`. A test proves none leak through `repr`, `str`, JSON dump or logs. |
| **Proper authentication** | JWT had no issuer, no unique id, and no password binding; any signing algorithm in the config was accepted. | **Fixed.** Required claims `exp`/`iat`/`iss`, random `jti`, fixed HMAC algorithm (`none` and asymmetric algorithms rejected at startup and at decode), password-bound tokens, `WWW-Authenticate` header, and the frontend now drops an expired session and sends the user to Login. Tests cover tampered, `alg=none`, expired, wrong-issuer, unsigned and missing-claim tokens. |
| **Update dependencies** | Nothing was pinned (a fresh build could pull a breaking release); two vulnerable packages. | **Fixed.** Tested version ranges (`~=` / `<next major`), `pip-audit` in CI, Dependabot weekly PRs, frontend `requirements.txt` (Streamlit capped at the tested line). |
| **Sanitize my forms** | Names and emails were stored as typed; job descriptions allowed some HTML tags (`<a>`, `<b>`); email subjects could contain line breaks (email-header injection). | **Fixed.** One shared sanitizer: HTML stripped, control and invisible/bidi characters removed. Names, job fields and email subjects are cleaned in the request schemas (so it cannot be forgotten in a new route). OTP field is digits only. |
| **Protect against XSS** | The frontend put server data (job text, names, emails) straight into HTML rendered with `unsafe_allow_html=True` in 20+ places: a stored XSS path from admin-written job text to every candidate. | **Fixed.** `frontend/safe.py` escapes every such value (also neutralises old stored rows). Admin job text is shown with `st.text`. Proven with an end-to-end test that stores `<script>`, `<img onerror>` and a phishing link in a job and checks nothing becomes live markup. Also: API responses carry a strict CSP. |
| **Turn off debug mode** | `/docs` and `/openapi.json` were public in production (a full map of your API); leftover `st.write("Selected Job ID")` / `st.json(...)` debug output in the UI; Streamlit would show Python stack traces to visitors. | **Fixed.** Docs off in production unless `ENABLE_DOCS=true`; `debug=False` explicit; debug UI output removed; `.streamlit/config.toml` sets `showErrorDetails = "none"`; noisy HTTP-client logging silenced. |
| **Full security audit** | This document. | Done. Remaining risks are listed in section 4. |
| **Check my env variables** | A key shorter than 32 characters was only a warning; nothing validated `ENVIRONMENT`, token lifetime, signing algorithm or upload size. | **Fixed.** Startup validation (refuses to start in production with a key under 32 chars, bad algorithm, nonsense limits, unknown `ENVIRONMENT`), `.env.example` rewritten, and `scripts/check_env.py`. |
| **Check for exposed files** | No route serves uploads (verified by a test). But the profile API returned the server's file path, and the profile page tried to use it as an image URL (broken, and a path leak). `.env`/db files had been committed. | **Fixed.** The path is never returned; `GET /users/me/picture` streams only the caller's own picture; `.gitignore` expanded; a test fails the build if `.env`, `.db`, keys or uploads become tracked. |
| **Protect admin routes** | Every admin route had the check, but only per function. | **Fixed.** Admin router carries the check at router level (a new route cannot be left open by accident), admin actions are written to the log (`AUDIT admin=...`), admin write routes are rate limited, tests cover it. |
| **Secure API endpoints** | Job list returned raw database objects and was unbounded; JSON bodies were unlimited; the email-sending path used an SMTP TLS setting that does **not verify the server certificate**. | **Fixed.** `response_model` on job routes, pagination (`limit` 1-500), 256 KB cap on JSON bodies (uploads keep their own limit) enforced even for chunked requests, SMTP now verifies certificates and hostnames, and every request schema has length limits and validators. |
| **Check CORS settings** | Default was `*` (any website could call the API from a browser). | **Fixed.** Default is only your frontend (`FRONTEND_URL`), plus localhost outside production. No credentials. `*` in production logs a warning. |
| **Add security headers** | None. | **Fixed.** `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy` (`default-src 'none'`), `Cache-Control: no-store`, HSTS in production. Present on every response including errors and CORS preflights. The `Server: uvicorn` banner is removed by the `--no-server-header` flag (section 1, item 4). |
| **Secure DB access** | Everything goes through the ORM with bound parameters (no raw SQL, verified). The connection did not force encryption. Supabase tables were reachable through its public REST API unless RLS is on. | **Fixed + Manual.** TLS enforced (`sslmode=require`) for remote Postgres unless the URL says otherwise; optional statement timeout; `scripts/enable_rls.py` (tested on a real PostgreSQL 16: RLS on for all tables, `anon` role locked out, app still works as table owner). Running it on Supabase is manual (section 1, item 3). |

---

## 3. Verified end to end (not just unit tests)

* The real backend ran against a real PostgreSQL 16 in production mode with row-level security enabled: signup, login, profile, jobs all worked; `/docs` returned 404; HSTS sent; the stored hash was `$argon2id$...`.
* `sslmode=require` was shown to be applied to a remote host, left alone when the URL already sets it, and skipped for localhost.
* Real HTTP response headers inspected with `curl`.
* Every Streamlit page rendered without errors against a live backend (including the admin panel after a real 2FA sign-in).
* A job row containing script tags, an `onerror` image and a phishing link was rendered as inert text.
* A garbage token made the frontend clear the session and go to Login.

---

## 4. Known limitations and residual risk

1. **Git history** still contains the old secrets until you do section 1. This is the largest remaining risk.
2. **Counters live in memory** (login lock-out, OTP attempts, chat allowances). They reset on restart and are not shared between multiple server processes. Fine for one Render instance; use Redis if you scale out.
3. **The 6-digit admin OTP is stored as plain text** for 5 minutes (the database column is only 10 characters wide, and a 6-digit code can be brute-forced from any hash anyway). It dies after 5 wrong guesses or 5 minutes.
4. **Streamlit Cloud controls the frontend's HTTP headers**, so the security headers above protect the API, not the Streamlit page itself. The page's token lives only in the server-side session.
5. **Account enumeration at signup**: "Email already registered" reveals that an address has an account. (Login, reset and OTP answers are identical for known and unknown accounts.) Fixing it properly means email-verified signup.
6. **A small timing difference** can remain between an unknown email and an account that still has an old bcrypt hash, until that user logs in once (then the hash is upgraded).
7. **Resumes are personal data** and are kept in the database (parsed text) and on the server disk. Consider a retention policy and object storage with encryption.
8. **Audit trail is log-based.** `AUDIT admin=...` lines go to the server log; there is no audit table.
9. **`st.components.v1.html`** (used for the chat bubble and home page) is deprecated in current Streamlit and slated for removal, which is why Streamlit is capped below 1.67. Migrate to the replacement before upgrading Streamlit.
10. **Database role**: use a dedicated Postgres user for the app rather than the project owner, with only the permissions it needs.
11. Not changed on purpose (not security): resume-fraud flags set at upload still do not reduce the 10% verification score, and the "semantic" score is lexical TF-IDF overlap.

---

## 4b. Added with the privacy release

* `DELETE /users/me` needs the password again, goes through the same wrong-password lock-out as login, answers **403** (not 401) for a wrong password so clients do not mistake it for an expired session, and refuses admin accounts.
* `GET /users/me/export` and `DELETE /users/me` are rate limited to 5 per hour.
* Unsubscribe tokens are signed, expire after a year, can only unsubscribe the address inside them and cannot be used to log in (and login tokens cannot unsubscribe anyone). The endpoint is POST-only so mail scanners cannot trigger it.
* Tables created by an update (`app/core/db_setup.py`) get row-level security switched on in the same step.
* All new routes appear in the access-control tests (anonymous callers are rejected everywhere except the explicitly listed public routes).

---

## 5. After deploying

* Everyone is signed out once (tokens now carry the password binding). Users just log in again; legacy bcrypt hashes upgrade silently.
* If the chat bubble stops working, set `CORS_ORIGINS` to the exact URL of your Streamlit app.
* `python -m scripts.scan_secrets --history` lists what is still in history (redacted).
