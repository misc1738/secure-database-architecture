import psycopg2
import os
import hashlib
from datetime import datetime

class SchemaManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="app_db",
            user="app_admin",
            password="your-password",
            host="localhost",
            sslmode="verify-full"
        )
        self.init_version_table()

    def init_version_table(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit.schema_versions (
                id SERIAL PRIMARY KEY,
                version VARCHAR(50),
                description TEXT,
                checksum VARCHAR(64),
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                applied_by VARCHAR(100)
            )
        """)
        self.conn.commit()

    def apply_migration(self, version, sql_content, description):
        cur = self.conn.cursor()
        checksum = hashlib.sha256(sql_content.encode()).hexdigest()
        
        try:
            cur.execute(sql_content)
            cur.execute("""
                INSERT INTO audit.schema_versions 
                (version, description, checksum, applied_by)
                VALUES (%s, %s, %s, current_user)
            """, (version, description, checksum))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()