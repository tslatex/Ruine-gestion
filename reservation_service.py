from models import Reservation, Produit, Client, db
from services.vente_service import VenteService
from datetime import datetime

class ReservationService:
    @staticmethod
    def creer_reservation(produit_id, client_id, quantite, date_limite=None, notes=""):
        """Créer une nouvelle réservation"""
        try:
            produit = Produit.query.get(produit_id)
            client = Client.query.get(client_id)
            
            if not produit:
                raise ValueError("Produit non trouvé")
            if not client:
                raise ValueError("Client non trouvé")
            
            reservation = Reservation(
                produit_id=produit_id,
                client_id=client_id,
                quantite=quantite,
                date_limite=date_limite,
                notes=notes
            )
            
            db.session.add(reservation)
            db.session.commit()
            
            return reservation
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def modifier_statut_reservation(reservation_id, nouveau_statut, notes=""):
        """Modifier le statut d'une réservation"""
        try:
            reservation = Reservation.query.get(reservation_id)
            if not reservation:
                raise ValueError("Réservation non trouvée")
            
            reservation.statut = nouveau_statut
            if notes:
                reservation.notes = notes
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def confirmer_reservation(reservation_id):
        """Confirmer une réservation et créer la vente correspondante"""
        try:
            reservation = Reservation.query.get(reservation_id)
            if not reservation:
                raise ValueError("Réservation non trouvée")
            
            if reservation.statut != "En attente":
                raise ValueError("La réservation n'est pas en attente")
            
            # Créer la vente
            vente = VenteService.creer_vente(
                reservation.produit_id,
                reservation.quantite,
                reservation.client_id
            )
            
            if vente:
                # Marquer la réservation comme confirmée
                reservation.statut = "Confirmé"
                db.session.commit()
                return True
            else:
                # Stock insuffisant
                return False
                
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_reservations_par_statut(statut):
        """Obtenir les réservations par statut"""
        return Reservation.query.filter_by(statut=statut).all()
    
    @staticmethod
    def get_reservations_expirees():
        """Obtenir les réservations expirées"""
        maintenant = datetime.now()
        return Reservation.query.filter(
            Reservation.date_limite < maintenant,
            Reservation.statut == "En attente"
        ).all()
    
    @staticmethod
    def get_statistiques_reservations():
        """Obtenir les statistiques des réservations"""
        total_reservations = Reservation.query.count()
        reservations_en_attente = Reservation.query.filter_by(statut="En attente").count()
        reservations_confirmees = Reservation.query.filter_by(statut="Confirmé").count()
        reservations_annulees = Reservation.query.filter_by(statut="Annulé").count()
        
        return {
            'total_reservations': total_reservations,
            'en_attente': reservations_en_attente,
            'confirmees': reservations_confirmees,
            'annulees': reservations_annulees
        }
