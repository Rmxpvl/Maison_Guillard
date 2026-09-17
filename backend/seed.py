import os

from dotenv import load_dotenv

load_dotenv()

from app.database import SessionLocal
from app.models.admin import Admin
from app.services import auth_service


def main():
    email = os.environ["SEED_ADMIN_EMAIL"]
    password = os.environ["SEED_ADMIN_PASSWORD"]

    db = SessionLocal()
    try:
        existing = db.query(Admin).filter(Admin.email == email).first()
        if existing:
            print(f"Admin {email} already exists, skipping.")
            return

        admin = Admin(email=email, password_hash=auth_service.hash_password(password))
        db.add(admin)
        db.commit()
        print(f"Created admin account for {email}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()