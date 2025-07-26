# create_tables.py

from app import create_app, db

# Create an app instance
app = create_app()

# Use the app context to access the database
with app.app_context():
    print("Dropping all tables (if they exist)...")
    db.drop_all()  # This ensures we have a clean slate
    print("Creating all tables from models...")
    db.create_all() # This creates all tables based on your current models
    print("✅ Tables created successfully!")