import psycopg2
import json
from datetime import datetime, timedelta
import pandas as pd

class ComplianceReport:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="app_db",
            user="auditor",
            password="your-password",
            host="localhost",
            sslmode="verify-full"
        )

    def generate_gdpr_report(self):
        cur = self.conn.cursor()
        
        # Check for data access patterns
        cur.execute("""
            SELECT username, COUNT(*) as access_count,
                   array_agg(DISTINCT table_name) as accessed_tables
            FROM audit.activity_log
            WHERE timestamp > now() - interval '30 days'
            GROUP BY username
        """)
        
        access_patterns = cur.fetchall()
        
        # Check for data retention compliance
        cur.execute("""
            SELECT COUNT(*) 
            FROM app.users 
            WHERE created_at < now() - interval '5 years'
        """)
        
        old_records = cur.fetchone()[0]
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'access_patterns': access_patterns,
            'old_records': old_records,
            'compliance_status': 'compliant' if old_records == 0 else 'action_needed'
        }
        
        return report

    def generate_audit_trail(self, days=30):
        cur = self.conn.cursor()
        
        cur.execute("""
            SELECT timestamp, user_id, action, table_name
            FROM audit.activity_log
            WHERE timestamp > now() - interval %s day
            ORDER BY timestamp DESC
        """, (days,))
        
        return cur.fetchall()

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()