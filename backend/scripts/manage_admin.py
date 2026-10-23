"""Create / promote / demote admins and reset an admin password.

Self-service signup can only create candidates, so this is how admins exist.
Run it on a machine that can reach the database:

    cd backend
    export DATABASE_URL=postgresql://...   SECRET_KEY=anything-32-chars-or-more
    python -m scripts.manage_admin promote you@example.com
    python -m scripts.manage_admin create  you@example.com --name "Your Name"
    python -m scripts.manage_admin set-password you@example.com
    python -m scripts.manage_admin demote you@example.com
"""
import argparse
import getpass
import sys

from app.core.database import SessionLocal
from app.core.security import hash_password, password_problems
from app.models.user import User


def _ask_password() -> str:
    while True:
        first = getpass.getpass("New password: ")
        problems = password_problems(first)
        if problems:
            print("Password needs " + ", ".join(problems))
            continue
        if first != getpass.getpass("Repeat password: "):
            print("Passwords do not match.")
            continue
        return first


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=["promote", "demote", "create", "set-password"])
    parser.add_argument("email")
    parser.add_argument("--name", default="Administrator", help="full name (create only)")
    args = parser.parse_args()
    email = args.email.strip().lower()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()

        if args.action == "create":
            if user:
                print(f"{email} already exists - use 'promote' instead.")
                return 1
            db.add(User(full_name=args.name, email=email, password_hash=hash_password(_ask_password()),
                        role="admin", is_active=True))
            db.commit()
            print(f"Admin {email} created.")
            return 0

        if not user:
            print(f"No user with email {email}.")
            return 1

        if args.action == "promote":
            user.role = "admin"
        elif args.action == "demote":
            user.role = "candidate"
        elif args.action == "set-password":
            user.password_hash = hash_password(_ask_password())
            user.reset_token = None
            user.reset_token_expiry = None
        db.commit()
        print(f"Done: {args.action} {email} (role is now '{user.role}').")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
