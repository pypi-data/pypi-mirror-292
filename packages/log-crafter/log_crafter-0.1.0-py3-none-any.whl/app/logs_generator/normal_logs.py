import random
import datetime

def generate_auth_log():
    """Génère un log d'authentification normal."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_type = "Accepted password"
    user_id = random.choice(["alice", "bob", "charlie", "dave", "eve"])
    ip_address = f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"
    log_message = f"{timestamp} AUTH {event_type} for {user_id} from IP {ip_address}"
    return log_message

def generate_syslog_log():
    """Génère un log syslog normal."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    severity = random.choice(["INFO", "NOTICE"])
    service = random.choice(["sshd", "systemd", "nginx", "cron", "docker"])
    message = random.choice([
        "Service started successfully",
        "Configuration reloaded",
        "User logged out",
        "Scheduled task completed"
    ])
    log_message = f"{timestamp} {severity} {service}: {message}"
    return log_message

def generate_kern_log():
    """Génère un log de noyau normal."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_level = random.choice(["INFO", "NOTICE"])
    event = random.choice(["Driver loaded", "Network interface up", "File system mounted"])
    log_message = f"{timestamp} KERNEL {log_level}: {event}"
    return log_message

def generate_daemon_log():
    """Génère un log de daemon normal."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    daemon = random.choice(["sshd", "cron", "nginx", "mysql", "postfix"])
    status = random.choice(["started", "stopped", "restarted"])
    log_message = f"{timestamp} DAEMON {daemon}: Service {status}"
    return log_message

def generate_fail2ban_log():
    """Génère un log fail2ban normal."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    action = "Unban"
    ip_address = f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"
    jail = random.choice(["ssh", "apache", "nginx", "mysql"])
    log_message = f"{timestamp} FAIL2BAN {action} IP {ip_address} in {jail}"
    return log_message
