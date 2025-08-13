import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from services.export_service import ExportService

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler_thread = None
        self.running = False
    
    def daily_export_job(self):
        """Tâche d'export quotidien"""
        try:
            from flask import current_app
            with current_app.app_context():
                # Export des données de la veille
                yesterday = (datetime.now() - timedelta(days=1)).date()
                
                logger.info(f"Début de l'export quotidien pour {yesterday}")
                
                # Sauvegarder les exports
                files = ExportService.save_daily_exports(yesterday)
                
                logger.info(f"Export quotidien terminé avec succès:")
                logger.info(f"- CSV Ventes: {files['ventes_csv']}")
                logger.info(f"- CSV Stock: {files['stock_csv']}")
                logger.info(f"- PDF Ventes: {files['ventes_pdf']}")
                
                return files
                
        except Exception as e:
            logger.error(f"Erreur lors de l'export quotidien: {str(e)}")
            raise
    
    def weekly_summary_job(self):
        """Tâche de résumé hebdomadaire (optionnel)"""
        try:
            from flask import current_app
            with current_app.app_context():
                logger.info("Génération du résumé hebdomadaire")
                # Ici, on pourrait générer un résumé de la semaine
                # Pour l'instant, on log juste
                logger.info("Résumé hebdomadaire généré")
                
        except Exception as e:
            logger.error(f"Erreur lors du résumé hebdomadaire: {str(e)}")
    
    def setup_schedules(self):
        """Configuration des tâches programmées"""
        # Export quotidien à 23h30
        schedule.every().day.at("23:30").do(self.daily_export_job)
        
        # Résumé hebdomadaire le dimanche à 23h45
        schedule.every().sunday.at("23:45").do(self.weekly_summary_job)
        
        # Export de test toutes les 5 minutes (pour les tests)
        # Décommentez la ligne suivante pour tester
        # schedule.every(5).minutes.do(self.daily_export_job)
        
        logger.info("Tâches programmées configurées:")
        logger.info("- Export quotidien: tous les jours à 23h30")
        logger.info("- Résumé hebdomadaire: dimanche à 23h45")
    
    def run_scheduler(self):
        """Exécute le planificateur en arrière-plan"""
        self.running = True
        logger.info("Démarrage du planificateur de tâches")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Vérifier toutes les minutes
            except Exception as e:
                logger.error(f"Erreur dans le planificateur: {str(e)}")
                time.sleep(60)
    
    def start(self):
        """Démarre le planificateur dans un thread séparé"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.warning("Le planificateur est déjà en cours d'exécution")
            return
        
        self.setup_schedules()
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Planificateur de tâches démarré")
    
    def stop(self):
        """Arrête le planificateur"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Planificateur de tâches arrêté")
    
    def run_manual_export(self, date=None):
        """Exécute manuellement un export pour une date donnée"""
        try:
            from flask import current_app
            with current_app.app_context():
                if not date:
                    date = datetime.now().date()
                
                logger.info(f"Export manuel pour {date}")
                files = ExportService.save_daily_exports(date)
                logger.info(f"Export manuel terminé avec succès")
                return files
                
        except Exception as e:
            logger.error(f"Erreur lors de l'export manuel: {str(e)}")
            raise

# Instance globale du planificateur
scheduler_service = SchedulerService()

def start_scheduler():
    """Fonction utilitaire pour démarrer le planificateur"""
    scheduler_service.start()

def stop_scheduler():
    """Fonction utilitaire pour arrêter le planificateur"""
    scheduler_service.stop()

def manual_export(date=None):
    """Fonction utilitaire pour un export manuel"""
    return scheduler_service.run_manual_export(date)