import yaml
import os
from app.logs_generator.normal_logs import (
    generate_auth_log,
    generate_syslog_log,
    generate_kern_log,
    generate_daemon_log,
    generate_fail2ban_log
)
from app.logs_generator.suspicious_logs import (
    generate_failed_auth_log,
    generate_privilege_escalation_log,
    generate_sql_injection_log,
    generate_phishing_log,
    generate_ddos_log
)

def load_yaml_config(file_path):
    """Charge la configuration à partir d'un fichier YAML."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def generate_logs_from_config(config):
    """Génère des logs en fonction de la configuration donnée."""
    log_generators = {
        'auth': generate_auth_log,
        'syslog': generate_syslog_log,
        'kern': generate_kern_log,
        'daemon': generate_daemon_log,
        'fail2ban': generate_fail2ban_log,
        'failed_auth': generate_failed_auth_log,
        'privilege_escalation': generate_privilege_escalation_log,
        'sql_injection': generate_sql_injection_log,
        'phishing': generate_phishing_log,
        'ddos': generate_ddos_log
    }

    for log_config in config['logs']:
        log_type = log_config.get('type')
        output_file = log_config.get('output_file')
        log_count = log_config.get('log_count', 100)

        if log_type not in log_generators:
            raise ValueError(f"Type de log inconnu: {log_type}")

        log_generator = log_generators[log_type]

        # Convertir le chemin en chemin absolu et vérifier l'existence
        abs_output_file = os.path.abspath(output_file)
        print(f"Chemin absolu du fichier de sortie: {abs_output_file}")
        os.makedirs(os.path.dirname(abs_output_file), exist_ok=True)

        # Écrire les logs dans le fichier
        try:
            with open(abs_output_file, 'w') as f:
                for _ in range(log_count):
                    log_entry = log_generator()
                    f.write(log_entry + '\n')
            print(f"Logs générés et enregistrés dans {abs_output_file}")
        except Exception as e:
            print(f"Erreur lors de l'écriture des logs: {e}")
