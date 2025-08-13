from models import Produit, MouvementStock, db
from datetime import datetime

class StockService:
    @staticmethod
    def ajouter_mouvement_stock(produit_id, type_mouvement, quantite, motif=""):
        """Ajouter un mouvement de stock (entrée ou sortie)"""
        try:
            produit = Produit.query.get(produit_id)
            if not produit:
                raise ValueError("Produit non trouvé")
            
            # Vérifier que la sortie ne dépasse pas le stock disponible
            if type_mouvement == 'sortie' and produit.stock < quantite:
                raise ValueError("Stock insuffisant pour cette sortie")
            
            # Créer le mouvement
            mouvement = MouvementStock(
                produit_id=produit_id,
                type_mouvement=type_mouvement,
                quantite=quantite,
                motif=motif
            )
            
            # Mettre à jour le stock du produit
            if type_mouvement == 'entree':
                produit.stock += quantite
            else:  # sortie
                produit.stock -= quantite
            
            db.session.add(mouvement)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_produits_stock_bas():
        """Obtenir la liste des produits avec un stock bas"""
        return Produit.query.filter(
            Produit.stock <= Produit.seuil_alerte
        ).all()
    
    @staticmethod
    def get_etat_stock():
        """Obtenir l'état général du stock"""
        produits = Produit.query.all()
        
        total_produits = len(produits)
        produits_stock_bas = len([p for p in produits if p.est_stock_bas])
        valeur_stock_total = sum(p.stock * p.prix_achat for p in produits)
        
        return {
            'total_produits': total_produits,
            'produits_stock_bas': produits_stock_bas,
            'valeur_stock_total': valeur_stock_total,
            'produits': produits
        }
    
    @staticmethod
    def reapprovisionner_automatique(produit_id, quantite_cible=None):
        """Réapprovisionner automatiquement un produit"""
        try:
            produit = Produit.query.get(produit_id)
            if not produit:
                raise ValueError("Produit non trouvé")
            
            if quantite_cible is None:
                quantite_cible = produit.seuil_alerte * 3  # 3x le seuil d'alerte
            
            quantite_a_ajouter = quantite_cible - produit.stock
            
            if quantite_a_ajouter > 0:
                return StockService.ajouter_mouvement_stock(
                    produit_id,
                    'entree',
                    quantite_a_ajouter,
                    f"Réapprovisionnement automatique - Cible: {quantite_cible}"
                )
            
            return True
            
        except Exception as e:
            raise e
