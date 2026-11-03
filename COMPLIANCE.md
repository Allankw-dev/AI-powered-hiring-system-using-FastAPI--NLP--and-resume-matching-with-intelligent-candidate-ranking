# Legal and compliance checklist

This implements the "20 things so your app doesn't get sued" checklist for AI Hiring System.
Everything below was written from what the app **actually does** (data collected, third parties used, how scoring works),
and the parts that can be tested are covered by automated tests (`backend/tests/test_legal.py`, `backend/tests/test_privacy.py`)
and were checked in a real browser (keyboard, contrast, accessibility scanner).

> **Important:** the legal texts in `/legal` are carefully drafted templates, **not legal advice**. Laws differ by country and change.
> Have a qualified lawyer (ideally one who knows Kenyan data-protection law) read them before you rely on them,
> especially if you recruit for real employers or serve people in the EU/UK.

## Before you go live (only you can do these)

| # | Action | Why |
|---|--------|-----|
| 1 | Set **`CONTACT_EMAIL`** on Render **and** in the Streamlit secrets (`CONTACT_EMAIL = "you@example.com"`) | The privacy policy promises a contact for data requests. Until it is set, the pages fall back to your GitHub profile. |
| 2 | Set **`API_PUBLIC_URL`** on Render to your API address (https) | Turns on the one-click unsubscribe header in emails (Gmail/Outlook show an "Unsubscribe" button). |
| 3 | Have a lawyer review `/legal/*.md` | See the note above. |
| 4 | Check whether you must **register with Kenya's Office of the Data Protection Commissioner** (odpc.go.ke) | Registration rules depend on the size and kind of data you process. |
| 5 | Decide how to treat **existing users** | Accounts created before this update have no stored consent record. Consider emailing them the new Terms and Privacy Policy, or adding a "please accept" step at next login. |
| 6 | Run `python -m scripts.enable_rls --apply` once if you have not yet | New tables get row-level security automatically; older ones need this one-off command. |

## The 20 items

| # | Item | Status | What was done and where to check it |
|---|------|--------|-------------------------------------|
| 1 | **Privacy policy** | Done | `legal/privacy-policy.md`, shown in the app (footer, "Privacy Policy"). Lists every data item, why, who processes it (Render, Streamlit Cloud, Supabase, Resend/Gmail, Anthropic, Google), retention, rights, automated scoring, children, complaints route. A test fails if the code starts talking to a provider the policy does not name. |
| 2 | **Terms of service** | Done | `legal/terms-of-service.md`: 18+, accounts, acceptable use, AI-score disclaimer, recruiter duties, free service, liability, deletion, Kenyan law. |
| 3 | **Refund policy** | Done (not applicable) | `legal/refund-policy.md`. The service is free, so it says there is nothing to refund and promises to publish a real policy before charging anything. |
| 4 | **Cookie policy** | Done | `legal/cookie-policy.md`, based on what was **measured** in a browser: one session cookie (`_streamlit_xsrf`), one local-storage key, and Google Fonts as the only third-party request. No analytics or advertising. |
| 5 | **Cookie consent banner** | Done (information notice) | `legal_pages.render_cookie_notice`. Because only strictly necessary storage is used, a consent gate is not required, so this is an information bar with two equally prominent buttons. A test fails if a tracker (Google Analytics, Hotjar, ...) is added without updating the policy. If you ever add tracking this **must** become an opt-in banner. |
| 6 | **Check form consents** | Done | Sign-up has two **separate, unticked** boxes (Terms+Privacy, and 18+). Both are required by the API (not just the form), and stored with the date and the version of the text (`consent_records` table). Nothing is bundled and no marketing consent is requested because no marketing is sent. |
| 7 | **No unnecessary data** | Done / note | We do not ask for gender, date of birth, address, phone, ID or payment details, and IP addresses are not stored in the database. The consent record stores no IP. *Note:* an old unused `users.sex` column still exists in the database (filled with a constant, never collected). It can only be dropped with a database migration, which is deliberately not automated. |
| 8 | **Audit third-party SDKs** | Done | There are **no** analytics, ad or tracking SDKs. Third parties are listed in the privacy policy and in `THIRD_PARTY_NOTICES.md`. The only browser-side third party is Google Fonts (your visitors' IP address reaches Google). To avoid that, self-host the two fonts. |
| 9 | **Remove dark patterns** | Done | Removed: the pulsing "new message" dot on the chat bubble (a fake notification), a decorative sign-up progress bar that implied "almost done", "Free Forever" and "hire better forever" promises. Added: an obvious "Delete my account" and "Download my data", an equal-weight cookie notice, an AI disclosure in the chat. |
| 10 | **Remove hidden fees** | Done | There are no prices anywhere in the app. The Terms and Refund Policy state clearly that it is free and that paid features would be announced first. |
| 11 | **Remove fake reviews** | Done | No testimonials existed. Fake social proof was removed ("500+ Jobs Matched"). |
| 12 | **Remove unsupported claims** | Done | Removed: "98% Match Accuracy", "10x Faster Hiring", "24/7 AI Active", "256-bit", "understands context" (the score is word overlap, not understanding), "verifies resume authenticity" (the checks are heuristics), "instantly". Home-page numbers are now checkable facts (4 scoring factors, 93 skills, free). The chat assistant's instructions were corrected too. `test_legal.py` fails if these phrases come back. |
| 13 | **Accessibility alt text** | Done | The only `<img>` has alt text; the decorative canvas is hidden from screen readers; embedded frames declare a language and title; a test enforces alt text on any future image. |
| 14 | **Fix colour contrast** | Done | Measured every text style in a real browser and raised those under WCAG AA 4.5:1 (footers 1.8:1, taglines 1.7:1, subtitles 2.6:1, policy links 2.7:1, ...). The accessibility scanner (axe-core) reports 0 issues on the home, login, sign-up, forgot-password, privacy and contact pages. |
| 15 | **Keyboard navigation** | Done | Home-page buttons are real, focusable controls that work with Enter and Space and show a 3px focus ring; the hidden auto-generated sidebar menu no longer adds invisible Tab stops; the chat closes with Escape; reduced-motion preference respected. Tested with real key presses in a browser (12/12). |
| 16 | **Add business details** | Done (needs your email) | "Contact" page and a footer line on every page: operator name, location, contact email. Email footers show them as well. Set `CONTACT_EMAIL` (see above). |
| 17 | **Age consent for kids' data** | Done | An "I am 18 or older" box is required (API and form) and stored. No date of birth is collected. The policy and Terms say the service is for adults and that accounts of minors will be deleted. This is a declaration; it does not verify age. |
| 18 | **Unsubscribe link in emails** | Done | Every email a recruiter sends to a candidate carries an unsubscribe link and the one-click `List-Unsubscribe` headers. Recruiters cannot email someone who unsubscribed (they are told why). Security emails (sign-in codes, password reset) are transactional and say so. |
| 19 | **License fonts/images** | Done | `THIRD_PARTY_NOTICES.md`: fonts (Orbitron and Exo 2, SIL Open Font License), 50 backend packages with licences, frontend packages. The app ships no image files (a test enforces a licence entry for any new one). Regenerate with `python -m scripts.generate_notices`. |
| 20 | **Data deletion request** | Done | Self-service in **Profile, Privacy & data**: download everything (JSON) and **permanently delete the account** (needs the password; erases the account, resumes and their files, applications, scores, emails and consent records, and renumbers other candidates' rankings). Also available by emailing the contact address. Extra: an export endpoint covers the "right of access". |

## Limits you should know about

* **Automated tests cannot prove full accessibility.** Scanners catch roughly a third of real-world problems. Streamlit's own widgets and the neon gradient headings are only partly checkable. Please try the site with a screen reader (NVDA on Windows, VoiceOver on iPhone) and with the keyboard alone.
* **Backups.** Deleted data may remain in your database provider's backups until they are overwritten (the privacy policy says so).
* **Admin accounts** cannot delete themselves through the app because they own job posts; remove them with `scripts/manage_admin.py` or in the database.
* **Chat messages** are sent to Anthropic/Google. The chat window says so and asks users not to share personal data.
* **Fonts** are loaded from Google, which reveals visitors' IP addresses to Google (disclosed in the policies). Self-hosting would remove this.
* **Age** is self-declared.
* **Contact email** falls back to your GitHub profile until `CONTACT_EMAIL` is set.

## How to check it yourself

```bash
cd backend
python -m pytest tests/test_legal.py tests/test_privacy.py     # compliance + privacy features
python -m scripts.check_env                                     # warns if CONTACT_EMAIL / API_PUBLIC_URL are missing
python -m scripts.generate_notices                              # refresh THIRD_PARTY_NOTICES.md
```
