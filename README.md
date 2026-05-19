# FileSharingSystem



## Features
- JWT auth with mobile login
- Custom user model
- Folder nesting
- File uploads
- Sharing and inherited permissions
- Activity logs
- PostgreSQL support

## Setup

```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py makemigrations accounts
python manage.py makemigrations storage
python manage.py makemigrations activity_logs
python manage.py migrate

python manage.py runserver
```
