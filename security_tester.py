import psycopg2
import ssl
import socket
import requests
from cryptography import x509
from datetime import datetime

class SecurityTester:
    def __init__(self):
        self.conn_params = {
            "dbname": "app_db",
            "user": "app_admin",
            "password": "your-password",
            "host": "localhost",
            "sslmode": "verify-full"
        }

    def test_ssl_configuration(self):
        context = ssl.create_default_context()
        with socket.create_connection(("localhost", 5432)) as sock:
            with context.wrap_socket(sock, server_hostname="localhost") as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                
                return {
                    'protocol_version': ssock.version(),
                    'cipher': ssock.cipher(),
                    'cert_expiry': expiry_date
                }

    def test_connection_security(self):
        results = []
        test_cases = [
            {"sslmode": "disable"},
            {"sslmode": "allow"},
            {"sslmode": "prefer"},
            {"sslmode": "require"},
            {"sslmode": "verify-ca"},
            {"sslmode": "verify-full"}
        ]

        for case in test_cases:
            try:
                test_params = self.conn_params.copy()
                test_params.update(case)
                conn = psycopg2.connect(**test_params)
                conn.close()
                results.append(f"Connection successful with {case['sslmode']}")
            except Exception as e:
                results.append(f"Connection failed with {case['sslmode']}: {str(e)}")

        return results