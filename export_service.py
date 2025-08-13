import os
import csv
import io
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from flask import current_app
from models import Vente, Produit, Client, MouvementStock

class ExportService:
    @staticmethod
    def get_daily_sales_data(date=None):
        """Récupère les données de vente pour une date donnée"""
        if not date:
            date = datetime.now().date()
        
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        from app import db
        ventes = db.session.query(Vente).filter(
            Vente.date_vente >= start_date,
            Vente.date_vente <= end_date
        ).all()
        
        return ventes
    
    @staticmethod
    def get_daily_stock_movements(date=None):
        """Récupère les mouvements de stock pour une date donnée"""
        if not date:
            date = datetime.now().date()
        
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        from app import db
        mouvements = db.session.query(MouvementStock).filter(
            MouvementStock.date_mouvement >= start_date,
            MouvementStock.date_mouvement <= end_date
        ).all()
        
        return mouvements
    
    @staticmethod
    def export_sales_to_csv(date=None):
        """Export des ventes en CSV"""
        if not date:
            date = datetime.now().date()
        
        ventes = ExportService.get_daily_sales_data(date)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # En-têtes
        writer.writerow([
            'Date de Vente', 'Client', 'Produit', 'Quantité', 
            'Prix Unitaire (Ar)', 'Total (Ar)', 'Bénéfice (Ar)'
        ])
        
        total_ventes = 0
        total_benefices = 0
        
        for vente in ventes:
            client_nom = vente.client.nom if vente.client else 'Client direct'
            produit_nom = vente.produit.nom if vente.produit else 'Produit supprimé'
            
            writer.writerow([
                vente.date_vente.strftime('%Y-%m-%d %H:%M'),
                client_nom,
                produit_nom,
                vente.quantite,
                f"{vente.prix_unitaire:,.0f}",
                f"{vente.total:,.0f}",
                f"{vente.benefice:,.0f}"
            ])
            
            total_ventes += vente.total
            total_benefices += vente.benefice
        
        # Ligne de total
        writer.writerow([])
        writer.writerow([
            'TOTAL', '', '', '', '',
            f"{total_ventes:,.0f}",
            f"{total_benefices:,.0f}"
        ])
        
        return output.getvalue()
    
    @staticmethod
    def export_stock_movements_to_csv(date=None):
        """Export des mouvements de stock en CSV"""
        if not date:
            date = datetime.now().date()
        
        mouvements = ExportService.get_daily_stock_movements(date)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # En-têtes
        writer.writerow([
            'Date', 'Produit', 'Type', 'Quantité', 
            'Raison', 'Stock Après'
        ])
        
        for mouvement in mouvements:
            produit_nom = mouvement.produit.nom if mouvement.produit else 'Produit supprimé'
            
            writer.writerow([
                mouvement.date_mouvement.strftime('%Y-%m-%d %H:%M'),
                produit_nom,
                mouvement.type_mouvement,
                mouvement.quantite,
                mouvement.raison or '',
                mouvement.stock_apres
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_sales_to_pdf(date=None):
        """Export des ventes en PDF"""
        if not date:
            date = datetime.now().date()
        
        ventes = ExportService.get_daily_sales_data(date)
        
        # Configuration du document PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.darkblue,
            alignment=1  # Centré
        )
        
        # Titre
        title = Paragraph(f"Rapport des Ventes - {date.strftime('%d/%m/%Y')}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        if not ventes:
            no_data = Paragraph("Aucune vente enregistrée pour cette date.", styles['Normal'])
            elements.append(no_data)
        else:
            # Données du tableau
            data = [['Date', 'Client', 'Produit', 'Qté', 'Prix Unit. (Ar)', 'Total (Ar)', 'Bénéfice (Ar)']]
            
            total_ventes = 0
            total_benefices = 0
            
            for vente in ventes:
                client_nom = vente.client.nom if vente.client else 'Client direct'
                produit_nom = vente.produit.nom if vente.produit else 'Produit supprimé'
                
                data.append([
                    vente.date_vente.strftime('%H:%M'),
                    client_nom[:15] + '...' if len(client_nom) > 15 else client_nom,
                    produit_nom[:15] + '...' if len(produit_nom) > 15 else produit_nom,
                    str(vente.quantite),
                    f"{vente.prix_unitaire:,.0f}",
                    f"{vente.total:,.0f}",
                    f"{vente.benefice:,.0f}"
                ])
                
                total_ventes += vente.total
                total_benefices += vente.benefice
            
            # Ligne de total
            data.append(['', '', '', '', 'TOTAL:', f"{total_ventes:,.0f}", f"{total_benefices:,.0f}"])
            
            # Création du tableau
            table = Table(data, colWidths=[0.8*inch, 1.2*inch, 1.2*inch, 0.5*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Résumé
            elements.append(Spacer(1, 20))
            summary = Paragraph(
                f"<b>Résumé du jour:</b><br/>"
                f"Nombre de ventes: {len(ventes)}<br/>"
                f"Chiffre d'affaires: {total_ventes:,.0f} Ar<br/>"
                f"Bénéfices totaux: {total_benefices:,.0f} Ar",
                styles['Normal']
            )
            elements.append(summary)
        
        # Footer
        elements.append(Spacer(1, 30))
        footer = Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} - RuineGestion Commerciale",
            styles['Normal']
        )
        elements.append(footer)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def save_daily_exports(date=None):
        """Sauvegarde les exports quotidiens dans des fichiers"""
        if not date:
            date = datetime.now().date()
        
        # Créer le dossier d'exports s'il n'existe pas
        export_dir = 'exports'
        daily_dir = os.path.join(export_dir, date.strftime('%Y-%m-%d'))
        os.makedirs(daily_dir, exist_ok=True)
        
        # Export CSV des ventes
        ventes_csv = ExportService.export_sales_to_csv(date)
        ventes_csv_path = os.path.join(daily_dir, f'ventes_{date.strftime("%Y%m%d")}.csv')
        with open(ventes_csv_path, 'w', encoding='utf-8') as f:
            f.write(ventes_csv)
        
        # Export CSV des mouvements de stock
        stock_csv = ExportService.export_stock_movements_to_csv(date)
        stock_csv_path = os.path.join(daily_dir, f'stock_mouvements_{date.strftime("%Y%m%d")}.csv')
        with open(stock_csv_path, 'w', encoding='utf-8') as f:
            f.write(stock_csv)
        
        # Export PDF des ventes
        ventes_pdf = ExportService.export_sales_to_pdf(date)
        ventes_pdf_path = os.path.join(daily_dir, f'rapport_ventes_{date.strftime("%Y%m%d")}.pdf')
        with open(ventes_pdf_path, 'wb') as f:
            f.write(ventes_pdf)
        
        return {
            'ventes_csv': ventes_csv_path,
            'stock_csv': stock_csv_path,
            'ventes_pdf': ventes_pdf_path,
            'date': date.strftime('%Y-%m-%d')
        }