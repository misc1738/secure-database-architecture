import psycopg2
import faker
import random
from datetime import datetime, timedelta

class DataAnonymizer:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="app_db",
            user="app_admin",
            password="your-password",
            host="localhost",
            sslmode="verify-full"
        )
        self.fake = faker.Faker()

    def anonymize_users_table(self):
        cur = self.conn.cursor()
        
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS app.users_anonymized (
                    LIKE app.users INCLUDING ALL
                )
            """)

            cur.execute("SELECT id FROM app.users")
            user_ids = cur.fetchall()

            for user_id in user_ids:
                cur.execute("""
                    INSERT INTO app.users_anonymized
                    SELECT 
                        id,
                        %s as username,
                        %s as email,
                        pgp_sym_encrypt(%s, current_setting('app.encryption_key')) as encrypted_ssn,
                        created_at,
                        updated_at
                    FROM app.users WHERE id = %s
                """, (
                    self.fake.user_name(),
                    self.fake.email(),
                    self.fake.ssn(),
                    user_id[0]
                ))

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()