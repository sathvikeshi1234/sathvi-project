# Django migration helper for emoji support
# Run this after updating the database with the SQL script

import os
import sys
import django

sys.path.append('c:/Users/arikatla/Documents/temp/sathvi project/ticket-management-')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def check_database_charset():
    """Check if database supports utf8mb4"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT DEFAULT_CHARACTER_SET_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = 'ticket_system'")
        result = cursor.fetchone()
        if result:
            charset = result[0]
            print(f"Database charset: {charset}")
            return charset.lower() == 'utf8mb4'
    return False

def check_table_charset():
    """Check if chatmessage table supports utf8mb4"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT CCSA.CHARACTER_SET_NAME 
            FROM information_schema.TABLES T, information_schema.COLLATION_CHARACTER_SET_APPLICABILITY CCSA 
            WHERE CCSA.COLLATION_NAME = T.TABLE_COLLATION 
            AND T.TABLE_SCHEMA = 'ticket_system' 
            AND T.TABLE_NAME = 'tickets_chatmessage'
        """)
        result = cursor.fetchone()
        if result:
            charset = result[0]
            print(f"ChatMessage table charset: {charset}")
            return charset.lower() == 'utf8mb4'
    return False

if __name__ == "__main__":
    print("Checking emoji support configuration...")
    
    db_support = check_database_charset()
    table_support = check_table_charset()
    
    print(f"Database supports utf8mb4: {db_support}")
    print(f"ChatMessage table supports utf8mb4: {table_support}")
    
    if db_support and table_support:
        print("✅ Emoji support is properly configured!")
    else:
        print("❌ Emoji support needs to be fixed!")
        print("Please run the fix_emoji_support.sql script in MySQL")
