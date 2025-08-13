from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Reservation, Produit, Client, db
from services.reservation_service import ReservationService
from datetime import datetime

reservations_bp = Blueprint('reservations', __name__)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@reservations_bp.route('/reservations')
@login_required
def liste_reservations():
    statut_filtre = request.args.get('statut', '')
    
    query = Reservation.query
    if statut_filtre:
        query = query.filter_by(statut=statut_filtre)
    
    reservations = query.order_by(Reservation.date_reservation.desc()).all()
    produits = Produit.query.all()
    clients = Client.query.all()
    
    return render_template('reservations.html', reservations=reservations,
                         produits=produits, clients=clients, statut_filtre=statut_filtre)

@reservations_bp.route('/reservations/ajouter', methods=['POST'])
@login_required
def ajouter_reservation():
    produit_id = int(request.form['produit_id'])
    client_id = int(request.form['client_id'])
    quantite = int(request.form['quantite'])
    date_limite_str = request.form.get('date_limite')
    notes = request.form.get('notes', '')
    
    date_limite = None
    if date_limite_str:
        date_limite = datetime.strptime(date_limite_str, '%Y-%m-%dT%H:%M')
    
    try:
        reservation = ReservationService.creer_reservation(
            produit_id, client_id, quantite, date_limite, notes
        )
        flash('Réservation créée avec succès', 'success')
    except Exception as e:
        flash(f'Erreur lors de la création: {str(e)}', 'error')
    
    return redirect(url_for('reservations.liste_reservations'))

@reservations_bp.route('/reservations/modifier/<int:reservation_id>', methods=['POST'])
@login_required
def modifier_statut_reservation(reservation_id):
    nouveau_statut = request.form['statut']
    notes = request.form.get('notes', '')
    
    try:
        if ReservationService.modifier_statut_reservation(reservation_id, nouveau_statut, notes):
            flash('Statut de réservation modifié avec succès', 'success')
        else:
            flash('Erreur lors de la modification', 'error')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('reservations.liste_reservations'))

@reservations_bp.route('/reservations/confirmer/<int:reservation_id>', methods=['POST'])
@login_required
def confirmer_reservation(reservation_id):
    try:
        if ReservationService.confirmer_reservation(reservation_id):
            flash('Réservation confirmée et vente créée avec succès', 'success')
        else:
            flash('Erreur lors de la confirmation (stock insuffisant)', 'error')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('reservations.liste_reservations'))

@reservations_bp.route('/reservations/supprimer/<int:reservation_id>', methods=['POST'])
@login_required
def supprimer_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    try:
        db.session.delete(reservation)
        db.session.commit()
        flash('Réservation supprimée avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la suppression', 'error')
    
    return redirect(url_for('reservations.liste_reservations'))

# API Routes
@reservations_bp.route('/api/reservations', methods=['GET'])
@jwt_required()
def api_liste_reservations():
    reservations = Reservation.query.order_by(Reservation.date_reservation.desc()).all()
    return jsonify([{
        'id': r.id,
        'produit_nom': r.produit.nom,
        'client_nom': r.client.nom,
        'quantite': r.quantite,
        'statut': r.statut,
        'date_reservation': r.date_reservation.isoformat(),
        'date_limite': r.date_limite.isoformat() if r.date_limite else None,
        'notes': r.notes
    } for r in reservations])

@reservations_bp.route('/api/reservations', methods=['POST'])
@jwt_required()
def api_ajouter_reservation():
    data = request.get_json()
    
    date_limite = None
    if data.get('date_limite'):
        date_limite = datetime.fromisoformat(data['date_limite'])
    
    try:
        reservation = ReservationService.creer_reservation(
            data['produit_id'],
            data['client_id'],
            data['quantite'],
            date_limite,
            data.get('notes', '')
        )
        
        return jsonify({
            'message': 'Réservation créée avec succès',
            'id': reservation.id
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Erreur: {str(e)}'}), 400

@reservations_bp.route('/api/reservations/<int:reservation_id>/confirmer', methods=['POST'])
@jwt_required()
def api_confirmer_reservation(reservation_id):
    try:
        success = ReservationService.confirmer_reservation(reservation_id)
        
        if success:
            return jsonify({'message': 'Réservation confirmée avec succès'})
        else:
            return jsonify({'message': 'Stock insuffisant'}), 400
            
    except Exception as e:
        return jsonify({'message': f'Erreur: {str(e)}'}), 400
