Here's a detailed `README.md` for your Python project:

---

# Library System API

This project is a Django-based API for managing a large library system. It was provided as a test task by ENA from Spotter.io.

## Table of Contents

- [Installation](#installation)
- [Database Setup](#database-setup)
- [Running the Project](#running-the-project)
- [Creating a Superuser](#creating-a-superuser)
- [Handling Large Index Files](#handling-large-index-files)

## Installation

1. **Clone the Repository:**

   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. **Create a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

1. **Configure Database in `settings.py`:**

   Open `settings.py` and update the `DATABASES` configuration with your PostgreSQL database details:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'DB_NAME',
           'USER': 'DB_USER',
           'PASSWORD': 'DB_PASS',
           'HOST': 'DB_HOST',
           'PORT': 'DB_PORT',
       }
   }
   ```

2. **Apply Migrations:**

   ```bash
   python manage.py migrate
   ```

## Running the Project

1. **Start the Django Development Server:**

   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://127.0.0.1:8000/`.

## Creating a Superuser

1. **Create a Superuser:**

   To access the Django admin interface, you'll need to create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

   Follow the prompts to set the username, email, and password.

2. **Accessing the Admin Interface:**

   Visit `http://127.0.0.1:8000/admin/` in your browser and log in with the superuser credentials.

## Handling Large Index Files

The following files are not included in the repository due to their large size:

- `book_ids.npy`
- `book_index.faiss`
- `checkpoint.npy`

### Instructions to Handle Large Files

1. **Download the Files:**

   If you have been provided with these files, download them and place them in the appropriate directory.

2. **Directory Structure:**

   Ensure the files are placed in the correct directories as expected by the code. If you are unsure, check the relevant parts of the code that reference these files.

   Example directory structure:

   ```
   project_root/
   
   ├── book_ids.npy
   ├── book_index.faiss
   └── checkpoint.npy
   ```

## Notes

- Ensure that your PostgreSQL service is running and that the database credentials match those in `settings.py`.
- This project was provided as a test task by ENA from Spotter.io.

---
