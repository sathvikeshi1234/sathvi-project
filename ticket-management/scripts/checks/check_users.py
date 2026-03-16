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

print("Available users:")
for u in User.objects.all():
    print("  - {} (superuser: {})".format(u.username, u.is_superuser))
    try:
        profile = u.userprofile
        role = profile.role.name if profile.role else "No role"
        print("    Role: {}".format(role))
    except UserProfile.DoesNotExist:
        print("    No profile")
    except Exception as e:
        print("    Error: {}".format(e))

print()
print("Available roles:")
for r in Role.objects.all():
    print("  - {}".format(r.name))
