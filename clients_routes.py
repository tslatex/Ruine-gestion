from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Client, db

clients_bp = Blueprint('clients', __name__)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@clients_bp.route('/clients')
@login_required
def liste_clients():
    search = request.args.get('search', '')
    if search:
        clients = Client.query.filter(Client.nom.contains(search)).all()
    else:
        clients = Client.query.all()
    
    return render_template('clients.html', clients=clients, search=search)

@clients_bp.route('/clients/ajouter', methods=['POST'])
@login_required
def ajouter_client():
    nom = request.form['nom']
    contact = request.form.get('contact', '')
    adresse = request.form.get('adresse', '')
    email = request.form.get('email', '')
    
    client = Client(
        nom=nom,
        contact=contact,
        adresse=adresse,
        email=email
    )
    
    try:
        db.session.add(client)
        db.session.commit()
        flash(f'Client "{nom}" ajouté avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de l\'ajout du client', 'error')
    
    return redirect(url_for('clients.liste_clients'))

@clients_bp.route('/clients/modifier/<int:client_id>', methods=['POST'])
@login_required
def modifier_client(client_id):
    client = Client.query.get_or_404(client_id)
    
    client.nom = request.form['nom']
    client.contact = request.form.get('contact', '')
    client.adresse = request.form.get('adresse', '')
    client.email = request.form.get('email', '')
    
    try:
        db.session.commit()
        flash('Client modifié avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la modification du client', 'error')
    
    return redirect(url_for('clients.liste_clients'))

@clients_bp.route('/clients/supprimer/<int:client_id>', methods=['POST'])
@login_required
def supprimer_client(client_id):
    client = Client.query.get_or_404(client_id)
    
    try:
        db.session.delete(client)
        db.session.commit()
        flash('Client supprimé avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la suppression du client', 'error')
    
    return redirect(url_for('clients.liste_clients'))

# API Routes
@clients_bp.route('/api/clients', methods=['GET'])
@jwt_required()
def api_liste_clients():
    clients = Client.query.all()
    return jsonify([{
        'id': c.id,
        'nom': c.nom,
        'contact': c.contact,
        'adresse': c.adresse,
        'email': c.email,
        'total_achats': c.total_achats,
        'created_at': c.created_at.isoformat()
    } for c in clients])

@clients_bp.route('/api/clients', methods=['POST'])
@jwt_required()
def api_ajouter_client():
    data = request.get_json()
    
    client = Client(
        nom=data['nom'],
        contact=data.get('contact', ''),
        adresse=data.get('adresse', ''),
        email=data.get('email', '')
    )
    
    try:
        db.session.add(client)
        db.session.commit()
        return jsonify({'message': 'Client créé avec succès', 'id': client.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la création'}), 400

@clients_bp.route('/api/clients/<int:client_id>', methods=['PUT'])
@jwt_required()
def api_modifier_client(client_id):
    client = Client.query.get_or_404(client_id)
    data = request.get_json()
    
    client.nom = data.get('nom', client.nom)
    client.contact = data.get('contact', client.contact)
    client.adresse = data.get('adresse', client.adresse)
    client.email = data.get('email', client.email)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Client modifié avec succès'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la modification'}), 400

@clients_bp.route('/api/clients/<int:client_id>', methods=['DELETE'])
@jwt_required()
def api_supprimer_client(client_id):
    client = Client.query.get_or_404(client_id)
    
    try:
        db.session.delete(client)
        db.session.commit()
        return jsonify({'message': 'Client supprimé avec succès'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la suppression'}), 400
