import unittest
from app.logs_generator.normal_logs import (
    generate_auth_log,
    generate_syslog_log,
    generate_kern_log,
    generate_daemon_log,
    generate_fail2ban_log
)

class TestNormalLogs(unittest.TestCase):

    def test_generate_auth_log(self):
        log = generate_auth_log()
        self.assertIn("AUTH", log)
        self.assertIn("Accepted password", log)
        self.assertIn("IP", log)

    def test_generate_syslog_log(self):
        log = generate_syslog_log()
        # Vérifier que le log contient soit "INFO" soit "NOTICE"
        self.assertTrue(any(level in log for level in ["INFO", "NOTICE"]))
        self.assertIn(":", log)

    def test_generate_kern_log(self):
        log = generate_kern_log()
        self.assertIn("KERNEL", log)
        # Vérifier que le log contient soit "INFO" soit "NOTICE"
        self.assertTrue(any(level in log for level in ["INFO", "NOTICE"]))
        self.assertIn(":", log)

    def test_generate_daemon_log(self):
        log = generate_daemon_log()
        self.assertIn("DAEMON", log)
        self.assertIn("Service", log)

    def test_generate_fail2ban_log(self):
        log = generate_fail2ban_log()
        self.assertIn("FAIL2BAN", log)
        self.assertIn("IP", log)
        self.assertIn("Unban", log)

if __name__ == '__main__':
    unittest.main()
