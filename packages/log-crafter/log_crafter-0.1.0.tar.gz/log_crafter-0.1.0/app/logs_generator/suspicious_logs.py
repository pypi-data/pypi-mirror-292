import random
import datetime

def generate_failed_auth_log():
    """Génère un log d'authentification échouée suspecte."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_type = "Failed password"
    user_id = random.choice(["root", "admin", "guest", "unknown"])
    ip_address = f"203.0.{random.randint(0, 255)}.{random.randint(0, 255)}"
    log_message = f"{timestamp} AUTH {event_type} for {user_id} from IP {ip_address}"
    return log_message

def generate_privilege_escalation_log():
    """Génère un log d'escalade de privilèges suspecte."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = random.choice(["user1", "user2", "user3"])
    log_message = f"{timestamp} SECURITY Privilege escalation attempt by {user_id}"
    return log_message

def generate_sql_injection_log():
    """Génère un log suspect d'injection SQL."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_address = f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"
    log_message = f"{timestamp} WEB SQL Injection attempt from IP {ip_address}"
    return log_message

def generate_phishing_log():
    """Génère un log suspect de phishing."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = random.choice(["user1", "user2", "user3"])
    log_message = f"{timestamp} EMAIL Phishing email detected for {user_id}"
    return log_message

def generate_ddos_log():
    """Génère un log suspect d'attaque DDoS."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_address = f"10.0.{random.randint(0, 255)}.{random.randint(0, 255)}"
    log_message = f"{timestamp} NETWORK DDoS attack detected from IP {ip_address}"
    return log_message
