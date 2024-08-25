import argparse
from app.utils import load_yaml_config, generate_logs_from_config

def main():
    parser = argparse.ArgumentParser(description='Générer des logs à partir d\'un fichier de configuration YAML.')
    parser.add_argument('config', type=str, help='Chemin vers le fichier de configuration YAML')
    
    args = parser.parse_args()
    config_file = args.config
    
    config = load_yaml_config(config_file)
    generate_logs_from_config(config)
