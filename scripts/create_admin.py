from __future__ import annotations

import argparse

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import AdminUser, UserRole


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create the first admin user.")
    parser.add_argument("--email", required=True, help="Admin email address")
    parser.add_argument("--password", required=True, help="Admin password")
    return parser.parse_args()


def create_admin(email: str, password: str) -> bool:
    normalized_email = email.strip().lower()
    with SessionLocal() as session:
        result = session.execute(select(AdminUser).where(AdminUser.email == normalized_email))
        existing = result.scalar_one_or_none()
        if existing is not None:
            print(f"Admin user {normalized_email} already exists; no duplicate was created.")
            return False

        admin = AdminUser(
            email=normalized_email,
            password_hash=hash_password(password),
            role=UserRole.admin.value,
            is_active=True,
        )
        session.add(admin)
        session.commit()
        print(f"Admin user {normalized_email} created.")
        return True


def main() -> None:
    args = parse_args()
    create_admin(args.email, args.password)


if __name__ == "__main__":
    main()
