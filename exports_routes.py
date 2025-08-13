from flask import Blueprint, request, jsonify, send_file, render_template, flash, redirect, url_for
from datetime import datetime, timedelta
import os
import tempfile
from services.export_service import ExportService
from services.scheduler_service import manual_export, scheduler_service
from routes.auth_routes import login_required

exports_bp = Blueprint('exports', __name__, url_prefix='/exports')

@exports_bp.route('/')
@login_required
def exports_dashboard():
    """Tableau de bord des exports"""
    try:
        # Liste des exports récents
        export_dir = 'exports'
        recent_exports = []
        
        if os.path.exists(export_dir):
            for date_folder in sorted(os.listdir(export_dir), reverse=True)[:7]:  # 7 derniers jours
                date_path = os.path.join(export_dir, date_folder)
                if os.path.isdir(date_path):
                    files = os.listdir(date_path)
                    recent_exports.append({
                        'date': date_folder,
                        'files': files,
                        'path': date_path
                    })
        
        return render_template('exports/dashboard.html', recent_exports=recent_exports)
    
    except Exception as e:
        flash(f'Erreur lors du chargement des exports: {str(e)}', 'error')
        return redirect(url_for('dashboard.dashboard'))

@exports_bp.route('/manual', methods=['POST'])
@login_required
def manual_export_route():
    """Déclenche un export manuel"""
    try:
        date_str = request.form.get('date')
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = datetime.now().date()
        
        files = manual_export(date)
        flash(f'Export réalisé avec succès pour le {date.strftime("%d/%m/%Y")}', 'success')
        
        return jsonify({
            'success': True,
            'message': f'Export réalisé pour le {date.strftime("%d/%m/%Y")}',
            'files': files
        })
    
    except Exception as e:
        flash(f'Erreur lors de l\'export: {str(e)}', 'error')
        return jsonify({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }), 500

@exports_bp.route('/download/csv/sales/<date>')
@login_required
def download_sales_csv(date):
    """Télécharge le CSV des ventes pour une date"""
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        csv_content = ExportService.export_sales_to_csv(date_obj)
        
        # Créer un fichier temporaire
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8')
        temp_file.write(csv_content)
        temp_file.close()
        
        filename = f'ventes_{date.replace("-", "")}.csv'
        
        def remove_file(response):
            os.unlink(temp_file.name)
            return response
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
    
    except Exception as e:
        flash(f'Erreur lors du téléchargement: {str(e)}', 'error')
        return redirect(url_for('exports.exports_dashboard'))

@exports_bp.route('/download/csv/stock/<date>')
@login_required
def download_stock_csv(date):
    """Télécharge le CSV des mouvements de stock pour une date"""
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        csv_content = ExportService.export_stock_movements_to_csv(date_obj)
        
        # Créer un fichier temporaire
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8')
        temp_file.write(csv_content)
        temp_file.close()
        
        filename = f'stock_mouvements_{date.replace("-", "")}.csv'
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
    
    except Exception as e:
        flash(f'Erreur lors du téléchargement: {str(e)}', 'error')
        return redirect(url_for('exports.exports_dashboard'))

@exports_bp.route('/download/pdf/sales/<date>')
@login_required
def download_sales_pdf(date):
    """Télécharge le PDF des ventes pour une date"""
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        pdf_content = ExportService.export_sales_to_pdf(date_obj)
        
        # Créer un fichier temporaire
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.write(pdf_content)
        temp_file.close()
        
        filename = f'rapport_ventes_{date.replace("-", "")}.pdf'
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        flash(f'Erreur lors du téléchargement: {str(e)}', 'error')
        return redirect(url_for('exports.exports_dashboard'))

@exports_bp.route('/api/status')
@login_required
def scheduler_status():
    """Statut du planificateur de tâches"""
    try:
        is_running = scheduler_service.running if scheduler_service.scheduler_thread else False
        
        return jsonify({
            'scheduler_running': is_running,
            'next_jobs': [],  # Ici on pourrait lister les prochaines tâches
            'last_export': None  # Ici on pourrait récupérer la date du dernier export
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exports_bp.route('/preview/sales/<date>')
@login_required
def preview_sales_data(date):
    """Aperçu des données de vente pour une date"""
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        ventes = ExportService.get_daily_sales_data(date_obj)
        
        total_ventes = sum(vente.total for vente in ventes)
        total_benefices = sum(vente.benefice for vente in ventes)
        
        return jsonify({
            'date': date,
            'count': len(ventes),
            'total_sales': total_ventes,
            'total_profit': total_benefices,
            'sales': [{
                'time': vente.date_vente.strftime('%H:%M'),
                'client': vente.client.nom if vente.client else 'Client direct',
                'produit': vente.produit.nom if vente.produit else 'Produit supprimé',
                'quantite': vente.quantite,
                'total': vente.total,
                'benefice': vente.benefice
            } for vente in ventes[:10]]  # Limite à 10 pour l'aperçu
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500