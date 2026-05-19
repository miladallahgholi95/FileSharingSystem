# FileSharingSystem

## Version: 1.1

A production-ready Django REST API for a private cloud file management and sharing platform.

---

## Developed By

### Milad Allahgholi

📧 miladallahgholi95@gmail.com

---

# 🚀 Features

- JWT Authentication using SimpleJWT
- Login with mobile number and password
- Custom user model
- User registration and profile management
- Secure password change
- Nested folder structure
- File upload and management
- File and folder sharing
- Direct and inherited permissions
- Recursive folder deletion
- Activity logging system
- PostgreSQL support
- Media file storage
- Clean and scalable architecture

---

# ⚙️ Setup

## 1. Clone Project

```bash
git clone https://github.com/miladallahgholi95/FileSharingSystem.git

cd FileSharingSystem
```

---

## 2. Create Virtual Environment

### Linux / macOS

```bash
python -m venv venv

source venv/bin/activate
```

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Run Migrations

```bash
python manage.py makemigrations accounts

python manage.py makemigrations storage

python manage.py makemigrations activity_logs

python manage.py migrate
```

---

## 6. Create Superuser

```bash
python manage.py createsuperuser
```

---

## 7. Run Server

```bash
python manage.py runserver
```

Server:

```text
http://127.0.0.1:8000/
```