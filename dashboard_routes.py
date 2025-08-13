from flask import Blueprint, render_template, session, redirect, url_for
from services.vente_service import VenteService
from services.stock_service import StockService
from models import Produit, Client, Vente, Livraison

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # Statistiques générales
    total_produits = Produit.query.count()
    total_clients = Client.query.count()
    total_ventes = Vente.query.count()
    livraisons_en_cours = Livraison.query.filter_by(statut='En cours').count()
    
    # Statistiques financières
    stats_financieres = VenteService.get_statistiques_financieres()
    
    # Produits en stock bas
    produits_stock_bas = StockService.get_produits_stock_bas()
    
    # Ventes récentes
    ventes_recentes = Vente.query.order_by(Vente.date_vente.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_produits=total_produits,
                         total_clients=total_clients,
                         total_ventes=total_ventes,
                         livraisons_en_cours=livraisons_en_cours,
                         stats_financieres=stats_financieres,
                         produits_stock_bas=produits_stock_bas,
                         ventes_recentes=ventes_recentes)
