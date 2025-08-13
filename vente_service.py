from models import Vente, Produit, Client, db
from datetime import datetime, timedelta
from sqlalchemy import func

class VenteService:
    @staticmethod
    def creer_vente(produit_id, quantite, client_id=None):
        """Créer une nouvelle vente"""
        try:
            produit = Produit.query.get(produit_id)
            if not produit:
                raise ValueError("Produit non trouvé")
            
            if produit.stock < quantite:
                return None  # Stock insuffisant
            
            # Créer la vente
            vente = Vente(
                produit_id=produit_id,
                client_id=client_id,
                quantite=quantite,
                prix_unitaire=produit.prix_unitaire,
                total=produit.prix_unitaire * quantite
            )
            
            # Mettre à jour le stock
            produit.stock -= quantite
            
            db.session.add(vente)
            db.session.commit()
            
            return vente
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_statistiques_financieres():
        """Obtenir les statistiques financières"""
        # Calculs des totaux
        total_ventes = db.session.query(func.sum(Vente.total)).scalar() or 0
        total_benefices = db.session.query(
            func.sum((Vente.prix_unitaire - Produit.prix_achat) * Vente.quantite)
        ).join(Produit).scalar() or 0
        
        nombre_ventes = Vente.query.count()
        
        # Ventes du jour
        aujourd_hui = datetime.now().date()
        ventes_jour = db.session.query(func.sum(Vente.total)).filter(
            func.date(Vente.date_vente) == aujourd_hui
        ).scalar() or 0
        
        # Ventes du mois
        debut_mois = datetime.now().replace(day=1)
        ventes_mois = db.session.query(func.sum(Vente.total)).filter(
            Vente.date_vente >= debut_mois
        ).scalar() or 0
        
        return {
            'total_ventes': total_ventes,
            'total_benefices': total_benefices,
            'nombre_ventes': nombre_ventes,
            'ventes_jour': ventes_jour,
            'ventes_mois': ventes_mois,
            'moyenne_vente': total_ventes / nombre_ventes if nombre_ventes > 0 else 0
        }
    
    @staticmethod
    def get_statistiques_par_periode(periode='mensuel'):
        """Obtenir les statistiques par période pour les graphiques"""
        if periode == 'journalier':
            # 7 derniers jours
            date_debut = datetime.now() - timedelta(days=7)
            format_date = func.date(Vente.date_vente)
        elif periode == 'hebdomadaire':
            # 8 dernières semaines
            date_debut = datetime.now() - timedelta(weeks=8)
            format_date = func.strftime('%Y-W%W', Vente.date_vente)
        else:  # mensuel
            # 12 derniers mois
            date_debut = datetime.now() - timedelta(days=365)
            format_date = func.strftime('%Y-%m', Vente.date_vente)
        
        stats = db.session.query(
            format_date.label('periode'),
            func.sum(Vente.total).label('total_ventes'),
            func.count(Vente.id).label('nombre_ventes'),
            func.sum(Vente.quantite).label('quantite_vendue')
        ).filter(
            Vente.date_vente >= date_debut
        ).group_by(format_date).order_by(format_date).all()
        
        return [{
            'periode': stat.periode,
            'total_ventes': float(stat.total_ventes or 0),
            'nombre_ventes': stat.nombre_ventes,
            'quantite_vendue': stat.quantite_vendue
        } for stat in stats]
    
    @staticmethod
    def format_ariary(montant):
        """Formater un montant en Ariary"""
        return f"{montant:,.0f} Ar".replace(',', ' ')
