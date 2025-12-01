import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import User, CustomerProfile

def create_admin_user():
    username = 'admin'
    password = 'adminpassword123'
    email = 'admin@example.com'
    
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_superuser(username=username, email=email, password=password)
        # Ensure customer profile exists even for admin (just in case)
        if not hasattr(user, 'customer_profile'):
             CustomerProfile.objects.create(user=user, address='Admin HQ', phone_number='000-000-0000')
        print(f"Superuser {username} created.")
    else:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"Superuser {username} password reset.")

if __name__ == '__main__':
    create_admin_user()
