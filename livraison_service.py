from models import Livraison, Client, db
from datetime import datetime

class LivraisonService:
    @staticmethod
    def creer_livraison(client_id, adresse, date_prevue=None, notes=""):
        """Créer une nouvelle livraison"""
        try:
            client = Client.query.get(client_id)
            if not client:
                raise ValueError("Client non trouvé")
            
            livraison = Livraison(
                client_id=client_id,
                adresse=adresse,
                date_prevue=date_prevue,
                notes=notes
            )
            
            db.session.add(livraison)
            db.session.commit()
            
            return livraison
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def modifier_statut_livraison(livraison_id, nouveau_statut, notes=""):
        """Modifier le statut d'une livraison"""
        try:
            livraison = Livraison.query.get(livraison_id)
            if not livraison:
                raise ValueError("Livraison non trouvée")
            
            livraison.statut = nouveau_statut
            if notes:
                livraison.notes = notes
            
            # Si la livraison est marquée comme livrée, enregistrer la date
            if nouveau_statut == "Livré":
                livraison.date_livraison = datetime.now()
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_livraisons_par_statut(statut):
        """Obtenir les livraisons par statut"""
        return Livraison.query.filter_by(statut=statut).all()
    
    @staticmethod
    def get_livraisons_en_cours():
        """Obtenir les livraisons en cours"""
        return LivraisonService.get_livraisons_par_statut("En cours")
    
    @staticmethod
    def get_statistiques_livraisons():
        """Obtenir les statistiques des livraisons"""
        total_livraisons = Livraison.query.count()
        livraisons_en_cours = Livraison.query.filter_by(statut="En cours").count()
        livraisons_livrees = Livraison.query.filter_by(statut="Livré").count()
        livraisons_annulees = Livraison.query.filter_by(statut="Annulé").count()
        
        return {
            'total_livraisons': total_livraisons,
            'en_cours': livraisons_en_cours,
            'livrees': livraisons_livrees,
            'annulees': livraisons_annulees
        }
