Step-by-Step Django Project Setup Guide
🪄 1. Create a Virtual Environment

This keeps your project dependencies isolated.

Windows:
python -m venv venv

Mac/Linux:
python3 -m venv venv

⚡ 2. Activate the Virtual Environment
Windows (Command Prompt or PowerShell):
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate


✅ You should now see (venv) at the beginning of your terminal prompt.

⚙️ 3. Install Required Packages

If you have a requirements.txt file:

pip install -r requirements.txt


If not, install manually:

pip install django
pip install pillow
pip install djangorestframework
pip install mysqlclient   # (Skip this if using SQLite)

✉️ 4. Configure Email for OTP (in settings.py)

Open your Django project’s settings.py file and add or update the following lines:

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_gmail@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'  # Use Gmail App Password

⚠️ Important:

Do not use your regular Gmail password.

Generate an App Password:

Go to https://myaccount.google.com/apppasswords

Choose your Gmail account.

Select Mail → Windows.

Copy the 16-character password and paste it in EMAIL_HOST_PASSWORD.

🧱 5. Database Setup
✅ If using SQLite (Default)

You can skip this step — Django automatically handles it.

🐬 If using MySQL

Edit your settings.py:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'secure_access_db',
        'USER': 'root',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


Then, create the database in MySQL:

CREATE DATABASE secure_access_db;

🏗 6. Run Migrations

Create and apply all necessary database tables.

python manage.py makemigrations
python manage.py migrate

👤 7. Create an Admin (Superuser)

This lets you access the Django admin panel.

python manage.py createsuperuser


Then follow the prompts:

Enter username

Enter email

Enter password

🌍 8. Run the Development Server

Start your Django project locally:

python manage.py runserver


Now open your browser and go to:

http://127.0.0.1:8000/


✅ You should now see your home/login page.
