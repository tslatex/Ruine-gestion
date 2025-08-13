from models import User, db

class AuthService:
    @staticmethod
    def create_user(username, password):
        """Créer un nouvel utilisateur"""
        try:
            # Vérifier si l'utilisateur existe déjà
            if User.query.filter_by(username=username).first():
                return None
            
            user = User(username=username)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            return None
    
    @staticmethod
    def authenticate_user(username, password):
        """Authentifier un utilisateur"""
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None
    
    @staticmethod
    def create_default_user():
        """Créer un utilisateur par défaut pour les tests"""
        if not User.query.first():
            default_user = User(username='admin')
            default_user.set_password('admin123')
            
            try:
                db.session.add(default_user)
                db.session.commit()
                print("Utilisateur par défaut créé: admin/admin123")
            except Exception as e:
                db.session.rollback()
                print(f"Erreur lors de la création de l'utilisateur par défaut: {e}")
