import unittest
from app.logs_generator.suspicious_logs import (
    generate_failed_auth_log,
    generate_privilege_escalation_log,
    generate_sql_injection_log,
    generate_phishing_log,
    generate_ddos_log
)

class TestSuspiciousLogs(unittest.TestCase):

    def test_generate_failed_auth_log(self):
        log = generate_failed_auth_log()
        self.assertIn("AUTH", log)
        self.assertIn("Failed password", log)
        self.assertIn("IP", log)

    def test_generate_privilege_escalation_log(self):
        log = generate_privilege_escalation_log()
        self.assertIn("SECURITY", log)
        self.assertIn("Privilege escalation", log)

    def test_generate_sql_injection_log(self):
        log = generate_sql_injection_log()
        self.assertIn("WEB", log)
        self.assertIn("SQL Injection", log)
        self.assertIn("IP", log)

    def test_generate_phishing_log(self):
        log = generate_phishing_log()
        self.assertIn("EMAIL", log)
        self.assertIn("Phishing", log)

    def test_generate_ddos_log(self):
        log = generate_ddos_log()
        self.assertIn("NETWORK", log)
        self.assertIn("DDoS attack", log)
        self.assertIn("IP", log)

if __name__ == '__main__':
    unittest.main()
