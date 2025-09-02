import os
from app import create_app, db
from app.models import User
from getpass import getpass

# Create an app instance using the default configuration
app = create_app()

# --- TO-RUN --- #
# Step 1 - set FLASK_APP=manage.py
# Step 2 - flask create-admin
# Step 3 - pytest
# ---  END    --- #


## Sets and per-enviorment test user credentials to be used by pytest 
@app.cli.command("create-admin")
def create_admin():
    """Creates a new admin user."""
    with app.app_context():
        username = input("Enter admin username: ")
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            print(f"Error: User '{username}' already exists.")
            return
        
        # Use getpass to securely prompt for the password
        password = getpass("Enter admin password: ")
        password_confirm = getpass("Confirm admin password: ")

        if password != password_confirm:
            print("Error: Passwords do not match.")
            return

        # Create the user object
        admin_user = User(username=username)
        admin_user.set_password(password)
        
        # Add to the database
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Admin user '{username}' created successfully.")