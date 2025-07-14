# Tucson Golden Doodles: Technology and Dependencies

This Flask-based web application is designed to showcase Golden Doodle puppies. It uses a modern technology stack to handle everything from the web interface and database interactions to cloud-based image storage.

### Core Framework: Flask

The application is built around **Flask**, a lightweight and flexible Python web framework. It provides the foundation for routing, request handling, and rendering templates. The core application is created using an application factory pattern (`create_app` function) in `app/__init__.py`, which makes the application more modular and easier to test and configure.

---

### Database and Data Management

* **Flask-SQLAlchemy**: This extension integrates the powerful **SQLAlchemy** Object-Relational Mapper (ORM) with Flask. Instead of writing raw SQL, we can define our database structure using Python classes called models (found in the `app/models/` directory). This makes database operations more intuitive and less error-prone. The application defines models for `Users`, `Puppies`, `Parents`, `Reviews`, and various site content sections.
* **Flask-Migrate**: To manage changes to the database schema over time, the project uses **Flask-Migrate**. This tool allows for incremental updates to the database structure as the application's models evolve.
* **PyMySQL**: This is the Python driver used to connect to a MySQL database, as specified in `requirements.txt` and configured in `config.py`.

---

### Admin and Authentication

* **Flask-Admin**: A secure admin interface is provided by **Flask-Admin**. This allows administrators to perform CRUD (Create, Read, Update, Delete) operations on the database models through a user-friendly web interface. The admin routes and views are configured in `app/routes/admin/routes.py` and `app/routes/admin/views.py`.
* **Flask-Login**: This extension handles user authentication for the admin panel. It manages user sessions, login/logout functionality, and protects admin routes from unauthorized access.

---

### Cloud Integration: AWS S3 for Image Storage ☁️

A key feature of this application is its integration with **Amazon Web Services (AWS)** for image management.

* **Boto3**: The official AWS SDK for Python, **boto3**, is used to communicate with AWS services.
* **S3 Image Uploads**: The application does not store user-uploaded images on the local server. Instead, it uploads them directly to an **Amazon S3 bucket**. The `app/utils/image_uploader.py` file contains the `upload_image` function, which handles this process. It securely names the files, uploads them to the specified S3 bucket, and returns the public URL, which is then stored in the database. This approach is highly scalable, reliable, and separates static assets from the application server.

---

### Frontend Technologies

* **Bootstrap 5**: The user interface is built using **Bootstrap**, a popular CSS framework. This ensures the website is responsive and looks great on all devices, from desktops to mobile phones. The base template in `app/templates/base.html` includes the Bootstrap CSS and JS bundles from a CDN.
* **Jinja2 Templates**: Flask uses the **Jinja2** templating engine to render dynamic HTML pages. This allows for embedding Python-like logic (loops, conditionals) directly into HTML files, as seen in templates like `index.html` and `parents.html`.

---

### Development and Testing

* **Python-dotenv**: This utility loads environment variables from a `.env` file into the application's environment. This is crucial for keeping sensitive information like database credentials and secret keys out of the source code, as shown in `config.py`.
* **Pytest**: The application's test suite is built using **pytest** and **pytest-flask**. This allows for writing clean, organized tests to ensure the application's models, routes, and other components work as expected. The testing configuration is defined in `pytest.ini` and fixtures are set up in `tests/conftest.py`.
