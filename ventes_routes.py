from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Vente, Produit, Client, db
from services.vente_service import VenteService
from datetime import datetime

ventes_bp = Blueprint('ventes', __name__)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@ventes_bp.route('/ventes')
@login_required
def liste_ventes():
    page = request.args.get('page', 1, type=int)
    ventes = Vente.query.order_by(Vente.date_vente.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    produits = Produit.query.filter(Produit.stock > 0).all()
    clients = Client.query.all()
    
    # Statistiques
    stats = VenteService.get_statistiques_financieres()
    
    return render_template('ventes.html', ventes=ventes, produits=produits, 
                         clients=clients, stats=stats)

@ventes_bp.route('/ventes/ajouter', methods=['POST'])
@login_required
def ajouter_vente():
    produit_id = int(request.form['produit_id'])
    client_id = request.form.get('client_id')
    if client_id:
        client_id = int(client_id)
    quantite = int(request.form['quantite'])
    
    try:
        vente = VenteService.creer_vente(produit_id, quantite, client_id)
        if vente:
            flash('Vente enregistrée avec succès', 'success')
        else:
            flash('Stock insuffisant pour cette vente', 'error')
    except Exception as e:
        flash(f'Erreur lors de l\'enregistrement de la vente: {str(e)}', 'error')
    
    return redirect(url_for('ventes.liste_ventes'))

@ventes_bp.route('/ventes/stats')
@login_required
def stats_ventes():
    periode = request.args.get('periode', 'mensuel')
    stats = VenteService.get_statistiques_par_periode(periode)
    return jsonify(stats)

# API Routes
@ventes_bp.route('/api/ventes', methods=['GET'])
@jwt_required()
def api_liste_ventes():
    ventes = Vente.query.order_by(Vente.date_vente.desc()).all()
    return jsonify([{
        'id': v.id,
        'produit_nom': v.produit.nom,
        'client_nom': v.client.nom if v.client else 'Client direct',
        'quantite': v.quantite,
        'prix_unitaire': v.prix_unitaire,
        'total': v.total,
        'benefice': v.benefice,
        'date_vente': v.date_vente.isoformat()
    } for v in ventes])

@ventes_bp.route('/api/ventes', methods=['POST'])
@jwt_required()
def api_ajouter_vente():
    data = request.get_json()
    
    try:
        vente = VenteService.creer_vente(
            data['produit_id'],
            data['quantite'],
            data.get('client_id')
        )
        
        if vente:
            return jsonify({
                'message': 'Vente créée avec succès',
                'id': vente.id,
                'total': vente.total
            }), 201
        else:
            return jsonify({'message': 'Stock insuffisant'}), 400
            
    except Exception as e:
        return jsonify({'message': f'Erreur: {str(e)}'}), 400

@ventes_bp.route('/api/ventes/stats', methods=['GET'])
@jwt_required()
def api_stats_ventes():
    periode = request.args.get('periode', 'mensuel')
    stats = VenteService.get_statistiques_par_periode(periode)
    return jsonify(stats)

@ventes_bp.route('/api/ventes/financiers', methods=['GET'])
@jwt_required()
def api_stats_financiers():
    stats = VenteService.get_statistiques_financieres()
    return jsonify(stats)
