import psycopg2
import logging
from datetime import datetime

logging.basicConfig(
    filename='maintenance.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DatabaseMaintenance:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="app_db",
            user="app_admin",
            password="your-password",
            host="localhost",
            sslmode="verify-full"
        )

    def vacuum_analyze(self):
        old_isolation = self.conn.isolation_level
        self.conn.set_isolation_level(0)
        cur = self.conn.cursor()
        
        try:
            cur.execute("VACUUM ANALYZE")
            logging.info("VACUUM ANALYZE completed successfully")
        except Exception as e:
            logging.error(f"VACUUM ANALYZE failed: {str(e)}")
        finally:
            self.conn.set_isolation_level(old_isolation)

    def clean_audit_logs(self):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                DELETE FROM audit.activity_log
                WHERE timestamp < now() - interval '1 year'
            """)
            self.conn.commit()
            logging.info("Old audit logs cleaned successfully")
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Audit log cleanup failed: {str(e)}")

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()