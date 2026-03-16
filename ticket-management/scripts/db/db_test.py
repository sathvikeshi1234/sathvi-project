import psycopg2
import sys

# --- CONFIGURATION ---
# Your Supabase project details
PROJECT_REF = "eaegoisnsdkdrpsywfsq"
PASSWORD = "Karthik_Ticket_2026_Secure"
REGION = "ap-south-1"

# Direct connection (IPv6 only - may not work on all networks)
DIRECT_URI = f"postgresql://postgres:{PASSWORD}@db.{PROJECT_REF}.supabase.co:5432/postgres?sslmode=require"

# Session Pooler (IPv4 compatible - port 5432)
SESSION_POOLER_URI = f"postgresql://postgres.{PROJECT_REF}:{PASSWORD}@aws-0-{REGION}.pooler.supabase.com:5432/postgres?sslmode=require"

# Transaction Pooler (IPv4 compatible - port 6543)
TRANSACTION_POOLER_URI = f"postgresql://postgres.{PROJECT_REF}:{PASSWORD}@aws-0-{REGION}.pooler.supabase.com:6543/postgres?sslmode=require"


def test_connection(name, uri):
    print(f"\n--- Testing {name} ---")
    # Hide password in output
    safe_uri = uri.replace(PASSWORD, "***")
    print(f"URI: {safe_uri}")

    try:
        conn = psycopg2.connect(uri, connect_timeout=10)
        print("✅ CONNECTION SUCCESSFUL!")

        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"📊 Postgres Version: {version[0][:50]}...")

        cur.close()
        conn.close()
        return True

    except psycopg2.OperationalError as e:
        print(f"❌ FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("SUPABASE CONNECTION TEST")
    print("=" * 50)
    print(f"Project Ref: {PROJECT_REF}")
    print(f"Region: {REGION}")

    # Try Direct connection first (may fail on IPv4-only networks)
    success = test_connection("Direct Connection (IPv6)", DIRECT_URI)

    if not success:
        # Try Session Pooler (IPv4 compatible)
        success = test_connection(
            "Session Pooler (IPv4, Port 5432)", SESSION_POOLER_URI
        )

    if not success:
        # Try Transaction Pooler
        test_connection("Transaction Pooler (IPv4, Port 6543)", TRANSACTION_POOLER_URI)

    print("\n" + "=" * 50)
