import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
import time
from pathlib import Path
import sys

def configurer_logging():
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')

        loggers = ['tennis_table']
        for logger_name in loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)
            logger.handlers.clear()
            logger.propagate = False

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
            )

            debug_handler = RotatingFileHandler(
                filename='logs/debug.log',
                maxBytes=2 * 1024 * 1024,  # 2 MB
                backupCount=3,
                encoding='utf-8'
            )
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(formatter)
            logger.addHandler(debug_handler)

            info_handler = RotatingFileHandler(
                filename='logs/info.log',
                maxBytes=1024 * 1024,  # 1 MB
                backupCount=2,
                encoding='utf-8'
            )
            info_handler.setLevel(logging.INFO)
            info_handler.setFormatter(formatter)
            logger.addHandler(info_handler)

            error_handler = TimedRotatingFileHandler(
                filename='logs/error.log',
                when='midnight',
                interval=1,
                backupCount=7,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            logger.addHandler(error_handler)

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

    except Exception as e:
        print(f"Erreur lors de la configuration du logging: {e}")
        raise

def nettoyer_vieux_logs():
    try:
        dossier_logs = Path('logs')
        if not dossier_logs.exists():
            return

        temps_actuel = time.time()
        strategies_nettoyage = {
            'debug.log*': 3 * 24 * 3600,
            'info.log*': 1 * 24 * 3600,
            'error.log*': 5 * 24 * 3600
        }

        for pattern, duree_retention in strategies_nettoyage.items():
            for fichier in dossier_logs.glob(pattern):
                age_fichier = temps_actuel - fichier.stat().st_mtime
                if age_fichier > duree_retention:
                    try:
                        fichier.unlink()
                        print(f"Fichier supprimé: {fichier}")
                    except Exception as e:
                        print(f"Impossible de supprimer {fichier}: {e}")

    except Exception as e:
        print(f"Erreur lors du nettoyage des logs: {e}")

def obtenir_statistiques_logs():
    try:
        dossier_logs = Path('logs')
        if not dossier_logs.exists():
            return {}

        stats = {
            'taille_totale': 0,
            'nombre_fichiers': 0,
            'fichiers': {}
        }

        for fichier in dossier_logs.glob('*.log*'):
            taille = fichier.stat().st_size
            modification = time.ctime(fichier.stat().st_mtime)
            stats['fichiers'][fichier.name] = {
                'taille': taille,
                'derniere_modification': modification
            }
            stats['taille_totale'] += taille
            stats['nombre_fichiers'] += 1

        return stats

    except Exception as e:
        print(f"Erreur lors de la récupération des statistiques: {e}")
        return {}