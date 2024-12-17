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
        for nom_logger in loggers:
            logger = logging.getLogger(nom_logger)
            logger.setLevel(logging.DEBUG)
            logger.handlers.clear()
            logger.propagate = False

            formateur = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
            )

            gestionnaire_debug = RotatingFileHandler(
                filename='logs/debug.log',
                maxBytes=2 * 1024 * 1024,  # 2 Mo
                backupCount=3,
                encoding='utf-8'
            )
            gestionnaire_debug.setLevel(logging.DEBUG)
            gestionnaire_debug.setFormatter(formateur)
            logger.addHandler(gestionnaire_debug)

            gestionnaire_info = RotatingFileHandler(
                filename='logs/info.log',
                maxBytes=1024 * 1024,  # 1 Mo
                backupCount=2,
                encoding='utf-8'
            )
            gestionnaire_info.setLevel(logging.INFO)
            gestionnaire_info.setFormatter(formateur)
            logger.addHandler(gestionnaire_info)

            gestionnaire_erreur = TimedRotatingFileHandler(
                filename='logs/error.log',
                when='midnight',
                interval=1,
                backupCount=7,
                encoding='utf-8'
            )
            gestionnaire_erreur.setLevel(logging.ERROR)
            gestionnaire_erreur.setFormatter(formateur)
            logger.addHandler(gestionnaire_erreur)

            gestionnaire_console = logging.StreamHandler(sys.stdout)
            gestionnaire_console.setLevel(logging.INFO)
            formateur_console = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            gestionnaire_console.setFormatter(formateur_console)
            logger.addHandler(gestionnaire_console)

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
            'debug.log*': 3 * 24 * 3600,  # 3 jours en secondes
            'info.log*': 1 * 24 * 3600,   # 1 jour en secondes
            'error.log*': 5 * 24 * 3600   # 5 jours en secondes
        }

        for motif, duree_retention in strategies_nettoyage.items():
            for fichier in dossier_logs.glob(motif):
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
