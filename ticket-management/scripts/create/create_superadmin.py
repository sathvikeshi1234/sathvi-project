import os
import sys
from pathlib import Path
import django

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainproject.settings")
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile, Role

# Create a superadmin user
user, created = User.objects.get_or_create(
    username="testsuperadmin",
    defaults={"email": "test@example.com", "is_superuser": True, "is_staff": True},
)
if created:
    user.set_password("admin123")
    user.save()
    print("Created superadmin user")
else:
    print("Superadmin user already exists")

# Create SuperAdmin role
role, role_created = Role.objects.get_or_create(name="SuperAdmin")
if role_created:
    print("Created SuperAdmin role")

# Assign role to user
profile, profile_created = UserProfile.objects.get_or_create(user=user)
profile.role = role
profile.save()
print("Assigned SuperAdmin role to user")

print("User: {}".format(user.username))
print("Is superuser: {}".format(user.is_superuser))
role_name = profile.role.name if profile.role else "No role"
print("Role: {}".format(role_name))
