# Tucson Golden Doodles 🐾

This Flask-based web application is designed to showcase Golden Doodle puppies. It uses a modern technology stack to handle everything from the web interface and database interactions to cloud-based image storage.

---

## Technology Stack 🛠️

The application is built with a robust and scalable technology stack, ensuring a seamless experience for both users and administrators.

### Core Framework & Backend

* **Flask**: A lightweight and flexible Python web framework that provides the foundation for routing, request handling, and rendering templates.
* **SQLAlchemy**: A powerful Object-Relational Mapper (ORM) that allows for database interactions using Python objects instead of raw SQL.
* **Flask-SQLAlchemy**: Integrates SQLAlchemy with Flask for a more streamlined development experience.
* **Alembic**: A database migration tool used with SQLAlchemy to manage and version database schemas.
* **Flask-Migrate**: Integrates Alembic with Flask for easier database migrations.
* **PyMySQL**: A Python driver for connecting to a MySQL database.

### Admin & Authentication

* **Flask-Admin**: Provides a secure and feature-rich administrative interface for CRUD (Create, Read, Update, Delete) operations on database models.
* **Flask-Login**: Manages user authentication for the admin panel, including user sessions and protecting routes from unauthorized access.

### Frontend

* **Bootstrap 5**: A popular CSS framework that ensures the website is responsive and looks great on all devices.
* **Jinja2**: A templating engine used by Flask to render dynamic HTML pages by embedding Python-like logic into HTML files.
* **Flask-WTF**: Integrates the WTForms library with Flask for creating and validating web forms.

### Cloud Integration ☁️

* **Amazon Web Services (AWS) S3**: Used for storing and managing all user-uploaded images. This approach is highly scalable, reliable, and separates static assets from the application server.
* **Boto3**: The official AWS SDK for Python, used to communicate with AWS services like S3.

### Development & Testing

* **Python-dotenv**: Loads environment variables from a `.env` file, keeping sensitive information like database credentials and secret keys out of the source code.
* **Pytest**: A testing framework used for writing clean, organized tests to ensure the application's components work as expected.
* **Flask-Caching**: Implements caching to improve performance by storing the results of expensive operations, like generating pre-signed S3 URLs.

---

## Feature Overview ✨

The application boasts a variety of features designed to make managing the website as easy as possible.

### For Site Visitors

* **Dynamic Homepage**: A multi-section homepage that includes a hero section, an "About Us" section, a list of available puppies, featured reviews, and a photo gallery.
* **Our Parents Page**: A dedicated page to showcase the sires and dams, complete with individual photo carousels, detailed descriptions, and a list of their past litters.
* **Our Puppies Page**: A page that lists all puppies, grouped by litter, with information about their parents and availability status.
* **Responsive Design**: A fully responsive design that works on all devices, from desktops to mobile phones, thanks to Bootstrap 5.

### For Administrators

* **Secure Admin Dashboard**: A password-protected admin dashboard for managing all aspects of the site's content.
* **Live Previews**: When editing content in the admin panel, a live preview is shown on the same page, allowing administrators to see their changes in real-time before saving. This is available for:
    * Parents
    * Puppies
    * Hero Section
    * About Section
    * Reviews
    * Gallery Images
    * Announcement Banner
* **CRUD Operations**: Full CRUD (Create, Read, Update, Delete) functionality for all major data models, including:
    * Parents
    * Puppies
    * Reviews
    * Hero Section
    * About Section
    * Gallery Images
    * Announcement Banner
* **Cloud Image Uploads**: Seamlessly upload images for parents, puppies, and site content directly to an AWS S3 bucket. The application handles generating responsive versions of images and creating secure, pre-signed URLs for display.
* **Dynamic Announcement Banner**: A site-wide announcement banner that can be linked to a specific litter to highlight new arrivals.
* **Featured Reviews**: The ability to mark certain reviews as "featured" to have them appear on the homepage.
