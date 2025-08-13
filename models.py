from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prix_achat = db.Column(db.Float, nullable=False, default=0)  # Prix d'achat pour calculer le bénéfice
    prix_unitaire = db.Column(db.Float, nullable=False)  # Prix de vente
    stock = db.Column(db.Integer, default=0)
    seuil_alerte = db.Column(db.Integer, default=10)  # Seuil pour alerte stock bas
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    ventes = db.relationship('Vente', backref='produit', lazy=True)
    mouvements_stock = db.relationship('MouvementStock', backref='produit', lazy=True)
    reservations = db.relationship('Reservation', backref='produit', lazy=True)
    
    @property
    def marge_benefice(self):
        return self.prix_unitaire - self.prix_achat
    
    @property
    def est_stock_bas(self):
        return self.stock <= self.seuil_alerte

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(50))
    adresse = db.Column(db.String(200))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    ventes = db.relationship('Vente', backref='client', lazy=True)
    livraisons = db.relationship('Livraison', backref='client', lazy=True)
    reservations = db.relationship('Reservation', backref='client', lazy=True)
    
    @property
    def total_achats(self):
        return sum(vente.total for vente in self.ventes)

class Vente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produit_id = db.Column(db.Integer, db.ForeignKey('produit.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)  # Prix au moment de la vente
    total = db.Column(db.Float, nullable=False)
    date_vente = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def benefice(self):
        if self.produit:
            return (self.prix_unitaire - self.produit.prix_achat) * self.quantite
        return 0

class MouvementStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produit_id = db.Column(db.Integer, db.ForeignKey('produit.id'), nullable=False)
    type_mouvement = db.Column(db.String(20), nullable=False)  # 'entree' ou 'sortie'
    quantite = db.Column(db.Integer, nullable=False)
    motif = db.Column(db.String(200))
    date_mouvement = db.Column(db.DateTime, default=datetime.utcnow)

class Livraison(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    adresse = db.Column(db.String(200), nullable=False)
    statut = db.Column(db.String(50), default="En cours")  # En cours, Livré, Annulé
    date_prevue = db.Column(db.DateTime)
    date_livraison = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produit_id = db.Column(db.Integer, db.ForeignKey('produit.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    statut = db.Column(db.String(50), default="En attente")  # En attente, Confirmé, Annulé
    date_reservation = db.Column(db.DateTime, default=datetime.utcnow)
    date_limite = db.Column(db.DateTime)
    notes = db.Column(db.Text)
