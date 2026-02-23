import os
from getpass import getpass

from app import create_app
from app.models import db, User

# Create an app instance using the default configuration
app = create_app()


@app.cli.command("create-admin")
def create_admin():
    """
    Creates or replaces the single admin user.

    This is an optional utility for local/dev or emergency recovery.
    Primary admin credentials are expected to come from environment variables
    and/or seed.py depending on your workflow.
    """
    with app.app_context():
        username = input("Enter admin username: ").strip()
        if not username:
            print("Error: username cannot be empty.")
            return

        password = getpass("Enter admin password: ")
        password_confirm = getpass("Confirm admin password: ")

        if password != password_confirm:
            print("Error: Passwords do not match.")
            return

        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f"User '{username}' already exists; updating password.")
            existing.set_password(password)
            db.session.commit()
            return

        admin_user = User(username=username)
        admin_user.set_password(password)
        db.session.add(admin_user)
        db.session.commit()

        print(f"Admin user '{username}' created successfully.")