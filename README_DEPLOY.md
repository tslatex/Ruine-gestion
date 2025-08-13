# Déploiement RuineGestion Commerciale sur Render

## Étapes de déploiement

### 1. Préparation GitHub
```bash
# Créer un nouveau repository GitHub
git init
git add .
git commit -m "Initial commit - RuineGestion Commerciale v1.0"
git branch -M main
git remote add origin https://github.com/VOTRE_USERNAME/ruine-gestion-commerciale.git
git push -u origin main
```

### 2. Déploiement sur Render

#### Option A: Déploiement automatique avec render.yaml
1. Connectez votre repository GitHub à Render
2. Le fichier `render.yaml` configurera automatiquement :
   - Service web Python 3.11.9
   - Base de données PostgreSQL
   - Variables d'environnement

#### Option B: Déploiement manuel
1. Créer un nouveau "Web Service" sur Render
2. Connecter votre repository GitHub
3. Configuration :
   - **Build Command**: `pip install -r render_requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`
   - **Python Version**: 3.11.9

4. Créer une base de données PostgreSQL sur Render
5. Ajouter les variables d'environnement :
   - `DATABASE_URL` (automatique depuis la DB)
   - `SESSION_SECRET` (générer une clé aléatoire)
   - `JWT_SECRET_KEY` (générer une clé aléatoire)

### 3. Variables d'environnement requises
```
DATABASE_URL=postgresql://user:password@host:port/database
SESSION_SECRET=votre_cle_secrete_session
JWT_SECRET_KEY=votre_cle_secrete_jwt
```

### 4. Fonctionnalités
- ✅ Gestion des ventes avec calculs automatiques en Ariary
- ✅ Gestion des stocks avec alertes de niveau bas
- ✅ Gestion des clients et historique d'achats
- ✅ Suivi des livraisons et réservations
- ✅ **Export automatique CSV/PDF quotidien à 23h30**
- ✅ API REST sécurisée avec authentification JWT
- ✅ Interface web responsive avec thème sombre
- ✅ Base de données PostgreSQL

### 5. Utilisation
- **Connexion par défaut** : admin / admin123
- **Export automatique** : Fichiers générés quotidiennement dans `/exports`
- **Export manuel** : Interface disponible dans le menu "Exports"

### 6. Architecture technique
- **Backend** : Flask + SQLAlchemy ORM
- **Base de données** : PostgreSQL
- **Authentification** : JWT + Sessions Flask + Bcrypt
- **Export** : ReportLab (PDF) + CSV native
- **Planificateur** : Module Schedule Python
- **Frontend** : Bootstrap 5 + Jinja2

### 7. Fichiers importants
- `main.py` : Point d'entrée de l'application
- `app.py` : Configuration Flask et initialisation
- `models.py` : Modèles de base de données
- `services/` : Logique métier (auth, ventes, stocks, exports)
- `routes/` : Contrôleurs API et web
- `templates/` : Templates HTML
- `static/` : Assets CSS/JS

### 8. Maintenance
- Les exports automatiques sont générés quotidiennement
- Les logs du planificateur sont visibles dans les logs Render
- La base de données PostgreSQL est sauvegardée automatiquement par Render

## Support
Pour toute question technique, consultez la documentation dans le code source.