from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Produit, MouvementStock, db
from services.stock_service import StockService

stocks_bp = Blueprint('stocks', __name__)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@stocks_bp.route('/stocks')
@login_required
def gestion_stocks():
    produits = Produit.query.all()
    mouvements = MouvementStock.query.order_by(MouvementStock.date_mouvement.desc()).limit(20).all()
    produits_stock_bas = StockService.get_produits_stock_bas()
    
    return render_template('stocks.html', 
                         produits=produits, 
                         mouvements=mouvements,
                         produits_stock_bas=produits_stock_bas)

@stocks_bp.route('/stocks/mouvement', methods=['POST'])
@login_required
def ajouter_mouvement():
    produit_id = int(request.form['produit_id'])
    type_mouvement = request.form['type_mouvement']
    quantite = int(request.form['quantite'])
    motif = request.form.get('motif', '')
    
    try:
        if StockService.ajouter_mouvement_stock(produit_id, type_mouvement, quantite, motif):
            flash(f'Mouvement de stock enregistré avec succès', 'success')
        else:
            flash('Erreur lors du mouvement de stock', 'error')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('stocks.gestion_stocks'))

@stocks_bp.route('/stocks/reapprovisionner/<int:produit_id>', methods=['POST'])
@login_required
def reapprovisionner(produit_id):
    quantite = int(request.form['quantite'])
    motif = request.form.get('motif', 'Réapprovisionnement')
    
    try:
        if StockService.ajouter_mouvement_stock(produit_id, 'entree', quantite, motif):
            flash('Réapprovisionnement effectué avec succès', 'success')
        else:
            flash('Erreur lors du réapprovisionnement', 'error')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('stocks.gestion_stocks'))

# API Routes
@stocks_bp.route('/api/stocks', methods=['GET'])
@jwt_required()
def api_etat_stocks():
    produits = Produit.query.all()
    return jsonify([{
        'id': p.id,
        'nom': p.nom,
        'stock': p.stock,
        'seuil_alerte': p.seuil_alerte,
        'est_stock_bas': p.est_stock_bas,
        'prix_unitaire': p.prix_unitaire
    } for p in produits])

@stocks_bp.route('/api/stocks/mouvements', methods=['GET'])
@jwt_required()
def api_mouvements_stock():
    mouvements = MouvementStock.query.order_by(MouvementStock.date_mouvement.desc()).limit(50).all()
    return jsonify([{
        'id': m.id,
        'produit_nom': m.produit.nom,
        'type_mouvement': m.type_mouvement,
        'quantite': m.quantite,
        'motif': m.motif,
        'date_mouvement': m.date_mouvement.isoformat()
    } for m in mouvements])

@stocks_bp.route('/api/stocks/mouvement', methods=['POST'])
@jwt_required()
def api_ajouter_mouvement():
    data = request.get_json()
    
    try:
        success = StockService.ajouter_mouvement_stock(
            data['produit_id'],
            data['type_mouvement'],
            data['quantite'],
            data.get('motif', '')
        )
        
        if success:
            return jsonify({'message': 'Mouvement de stock enregistré'}), 201
        else:
            return jsonify({'message': 'Erreur lors du mouvement'}), 400
            
    except Exception as e:
        return jsonify({'message': f'Erreur: {str(e)}'}), 400

@stocks_bp.route('/api/stocks/bas', methods=['GET'])
@jwt_required()
def api_stocks_bas():
    produits = StockService.get_produits_stock_bas()
    return jsonify([{
        'id': p.id,
        'nom': p.nom,
        'stock': p.stock,
        'seuil_alerte': p.seuil_alerte
    } for p in produits])
