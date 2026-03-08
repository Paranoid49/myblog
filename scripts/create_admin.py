from argparse import ArgumentParser

from sqlalchemy import select

import app.models  # noqa: F401
from app.core.db import SessionLocal
from app.services.auth_service import build_admin_user


def main() -> None:
    parser = ArgumentParser(description="Create initial admin user")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        existing_user = db.execute(select(app.models.User).where(app.models.User.username == args.username)).scalar_one_or_none()
        if existing_user:
            raise SystemExit("admin user already exists")

        user = build_admin_user(args.username, args.password)
        db.add(user)
        db.commit()
        print(f"created admin user: {user.username}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
