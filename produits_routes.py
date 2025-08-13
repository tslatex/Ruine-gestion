from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Produit, db
from services.stock_service import StockService

produits_bp = Blueprint('produits', __name__)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@produits_bp.route('/produits')
@login_required
def liste_produits():
    search = request.args.get('search', '')
    if search:
        produits = Produit.query.filter(Produit.nom.contains(search)).all()
    else:
        produits = Produit.query.all()
    
    return render_template('produits.html', produits=produits, search=search)

@produits_bp.route('/produits/ajouter', methods=['POST'])
@login_required
def ajouter_produit():
    nom = request.form['nom']
    prix_achat = float(request.form['prix_achat'])
    prix_unitaire = float(request.form['prix_unitaire'])
    stock_initial = int(request.form.get('stock_initial', 0))
    seuil_alerte = int(request.form.get('seuil_alerte', 10))
    
    produit = Produit(
        nom=nom,
        prix_achat=prix_achat,
        prix_unitaire=prix_unitaire,
        stock=stock_initial,
        seuil_alerte=seuil_alerte
    )
    
    try:
        db.session.add(produit)
        db.session.commit()
        flash(f'Produit "{nom}" ajouté avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de l\'ajout du produit', 'error')
    
    return redirect(url_for('produits.liste_produits'))

@produits_bp.route('/produits/modifier/<int:produit_id>', methods=['POST'])
@login_required
def modifier_produit(produit_id):
    produit = Produit.query.get_or_404(produit_id)
    
    produit.nom = request.form['nom']
    produit.prix_achat = float(request.form['prix_achat'])
    produit.prix_unitaire = float(request.form['prix_unitaire'])
    produit.seuil_alerte = int(request.form.get('seuil_alerte', 10))
    
    try:
        db.session.commit()
        flash('Produit modifié avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la modification du produit', 'error')
    
    return redirect(url_for('produits.liste_produits'))

@produits_bp.route('/produits/supprimer/<int:produit_id>', methods=['POST'])
@login_required
def supprimer_produit(produit_id):
    produit = Produit.query.get_or_404(produit_id)
    
    try:
        db.session.delete(produit)
        db.session.commit()
        flash('Produit supprimé avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la suppression du produit', 'error')
    
    return redirect(url_for('produits.liste_produits'))

# API Routes
@produits_bp.route('/api/produits', methods=['GET'])
@jwt_required()
def api_liste_produits():
    produits = Produit.query.all()
    return jsonify([{
        'id': p.id,
        'nom': p.nom,
        'prix_achat': p.prix_achat,
        'prix_unitaire': p.prix_unitaire,
        'stock': p.stock,
        'seuil_alerte': p.seuil_alerte,
        'est_stock_bas': p.est_stock_bas,
        'marge_benefice': p.marge_benefice
    } for p in produits])

@produits_bp.route('/api/produits', methods=['POST'])
@jwt_required()
def api_ajouter_produit():
    data = request.get_json()
    
    produit = Produit(
        nom=data['nom'],
        prix_achat=data['prix_achat'],
        prix_unitaire=data['prix_unitaire'],
        stock=data.get('stock', 0),
        seuil_alerte=data.get('seuil_alerte', 10)
    )
    
    try:
        db.session.add(produit)
        db.session.commit()
        return jsonify({'message': 'Produit créé avec succès', 'id': produit.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la création'}), 400

@produits_bp.route('/api/produits/<int:produit_id>', methods=['PUT'])
@jwt_required()
def api_modifier_produit(produit_id):
    produit = Produit.query.get_or_404(produit_id)
    data = request.get_json()
    
    produit.nom = data.get('nom', produit.nom)
    produit.prix_achat = data.get('prix_achat', produit.prix_achat)
    produit.prix_unitaire = data.get('prix_unitaire', produit.prix_unitaire)
    produit.seuil_alerte = data.get('seuil_alerte', produit.seuil_alerte)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Produit modifié avec succès'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la modification'}), 400

@produits_bp.route('/api/produits/<int:produit_id>', methods=['DELETE'])
@jwt_required()
def api_supprimer_produit(produit_id):
    produit = Produit.query.get_or_404(produit_id)
    
    try:
        db.session.delete(produit)
        db.session.commit()
        return jsonify({'message': 'Produit supprimé avec succès'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la suppression'}), 400
