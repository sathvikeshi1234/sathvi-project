import os
import sys
from pathlib import Path
import django

# Set up Django environment
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainproject.settings")
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'core%';"
    )
    tables = cursor.fetchall()
    print("Core tables:", [t[0] for t in tables])
