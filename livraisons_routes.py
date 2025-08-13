from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Livraison, Client, db
from services.livraison_service import LivraisonService
from datetime import datetime

livraisons_bp = Blueprint('livraisons', __name__)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@livraisons_bp.route('/livraisons')
@login_required
def liste_livraisons():
    statut_filtre = request.args.get('statut', '')
    
    query = Livraison.query
    if statut_filtre:
        query = query.filter_by(statut=statut_filtre)
    
    livraisons = query.order_by(Livraison.created_at.desc()).all()
    clients = Client.query.all()
    
    return render_template('livraisons.html', livraisons=livraisons, 
                         clients=clients, statut_filtre=statut_filtre)

@livraisons_bp.route('/livraisons/ajouter', methods=['POST'])
@login_required
def ajouter_livraison():
    client_id = int(request.form['client_id'])
    adresse = request.form['adresse']
    date_prevue_str = request.form.get('date_prevue')
    notes = request.form.get('notes', '')
    
    date_prevue = None
    if date_prevue_str:
        date_prevue = datetime.strptime(date_prevue_str, '%Y-%m-%dT%H:%M')
    
    try:
        livraison = LivraisonService.creer_livraison(client_id, adresse, date_prevue, notes)
        flash('Livraison programmée avec succès', 'success')
    except Exception as e:
        flash(f'Erreur lors de la programmation: {str(e)}', 'error')
    
    return redirect(url_for('livraisons.liste_livraisons'))

@livraisons_bp.route('/livraisons/modifier/<int:livraison_id>', methods=['POST'])
@login_required
def modifier_statut_livraison(livraison_id):
    nouveau_statut = request.form['statut']
    notes = request.form.get('notes', '')
    
    try:
        if LivraisonService.modifier_statut_livraison(livraison_id, nouveau_statut, notes):
            flash('Statut de livraison modifié avec succès', 'success')
        else:
            flash('Erreur lors de la modification', 'error')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('livraisons.liste_livraisons'))

@livraisons_bp.route('/livraisons/supprimer/<int:livraison_id>', methods=['POST'])
@login_required
def supprimer_livraison(livraison_id):
    livraison = Livraison.query.get_or_404(livraison_id)
    
    try:
        db.session.delete(livraison)
        db.session.commit()
        flash('Livraison supprimée avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la suppression', 'error')
    
    return redirect(url_for('livraisons.liste_livraisons'))

# API Routes
@livraisons_bp.route('/api/livraisons', methods=['GET'])
@jwt_required()
def api_liste_livraisons():
    livraisons = Livraison.query.order_by(Livraison.created_at.desc()).all()
    return jsonify([{
        'id': l.id,
        'client_nom': l.client.nom,
        'adresse': l.adresse,
        'statut': l.statut,
        'date_prevue': l.date_prevue.isoformat() if l.date_prevue else None,
        'date_livraison': l.date_livraison.isoformat() if l.date_livraison else None,
        'notes': l.notes,
        'created_at': l.created_at.isoformat()
    } for l in livraisons])

@livraisons_bp.route('/api/livraisons', methods=['POST'])
@jwt_required()
def api_ajouter_livraison():
    data = request.get_json()
    
    date_prevue = None
    if data.get('date_prevue'):
        date_prevue = datetime.fromisoformat(data['date_prevue'])
    
    try:
        livraison = LivraisonService.creer_livraison(
            data['client_id'],
            data['adresse'],
            date_prevue,
            data.get('notes', '')
        )
        
        return jsonify({
            'message': 'Livraison créée avec succès',
            'id': livraison.id
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Erreur: {str(e)}'}), 400

@livraisons_bp.route('/api/livraisons/<int:livraison_id>/statut', methods=['PUT'])
@jwt_required()
def api_modifier_statut(livraison_id):
    data = request.get_json()
    
    try:
        success = LivraisonService.modifier_statut_livraison(
            livraison_id,
            data['statut'],
            data.get('notes', '')
        )
        
        if success:
            return jsonify({'message': 'Statut modifié avec succès'})
        else:
            return jsonify({'message': 'Erreur lors de la modification'}), 400
            
    except Exception as e:
        return jsonify({'message': f'Erreur: {str(e)}'}), 400
