# LogCraft

LogCraft est une bibliothèque Python pour générer des fichiers de logs normaux et suspects. Elle est conçue pour simuler des environnements réels en créant des fichiers de logs diversifiés, utilisés notamment pour l'entraînement d'IA dans des systèmes de détection d'intrusion.

## Fonctionnalités

- Génération de logs d'authentification (auth.log)
- Génération de logs de syslog (syslog.log)
- Génération de logs d'échec d'authentification (failed_auth.log)
- Génération de logs d'escalade de privilèges, d'injection SQL, de phishing, et d'attaque DDoS
- Configuration via un fichier YAML pour spécifier le type de log, le fichier de sortie, et le nombre de logs à générer

## Installation

Vous pouvez installer LogCraft directement depuis PyPI (à venir) ou en clonant ce dépôt.

```bash
pip install logcraft
```
## Utilisation

### Configuration

Créez un fichier de configuration YAML, par exemple logs_config.yml :

```yml
logs:
  - type: "auth"
    output_file: "./logs/auth.log"
    log_count: 1000

  - type: "failed_auth"
    output_file: "./logs/failed_auth.log"
    log_count: 100
```
## Génération de Logs

Utilisez le module CLI pour générer des logs basés sur votre fichier de configuration :

```bash
python -m app.main config/logs_config.yml
```