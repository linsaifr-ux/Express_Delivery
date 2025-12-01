import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import User

def check_admin_user():
    username = 'admin'
    try:
        user = User.objects.get(username=username)
        print(f"User: {user.username}")
        print(f"Email: {user.email}")
        print(f"Is Active: {user.is_active}")
        print(f"Is Staff: {user.is_staff}")
        print(f"Is Superuser: {user.is_superuser}")
        print(f"Password set: {user.has_usable_password()}")
        # Check password hash start to see if it looks normal (not printing full hash)
        print(f"Password hash prefix: {user.password[:20]}")
    except User.DoesNotExist:
        print(f"User {username} does not exist.")

if __name__ == '__main__':
    check_admin_user()
