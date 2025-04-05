import psycopg2
import logging
from datetime import datetime
import smtplib
from email.message import EmailMessage

logging.basicConfig(
    filename='database_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_database_health():
    try:
        conn = psycopg2.connect(
            dbname="app_db",
            user="app_admin",
            password="your-password",
            host="localhost",
            sslmode="verify-full"
        )
        
        cur = conn.cursor()
        
        # Check for failed login attempts
        cur.execute("""
            SELECT count(*) 
            FROM pg_catalog.pg_auth_entries 
            WHERE NOT success 
            AND date > now() - interval '1 hour'
        """)
        failed_logins = cur.fetchone()[0]
        
        if failed_logins > 10:
            alert("High number of failed login attempts detected!")
            
        # Check database size
        cur.execute("SELECT pg_database_size('app_db')/1024/1024 as size_mb;")
        db_size = cur.fetchone()[0]
        
        if db_size > 10000:  # Alert if DB size > 10GB
            alert("Database size exceeds threshold!")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        logging.error(f"Monitoring error: {str(e)}")
        alert(f"Database monitoring failed: {str(e)}")

def alert(message):
    logging.warning(message)
    # Add your alert mechanism here (email, SMS, etc.)