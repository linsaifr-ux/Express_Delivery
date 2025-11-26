
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import User, CustomerProfile

def create_test_user():
    username = 'web_test_user'
    password = 'password123'
    email = 'webtest@example.com'
    
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, email=email, password=password)
        CustomerProfile.objects.create(user=user, address='123 Web Test St', phone_number='555-WEB-TEST')
        print(f"User {username} created.")
    else:
        print(f"User {username} already exists.")

if __name__ == '__main__':
    create_test_user()
