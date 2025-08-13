/**
 * RuineGestion - Application JavaScript
 * Fonctionnalités communes pour l'application de gestion commerciale
 */

// Configuration globale
const RuineGestion = {
    // Format de devise Ariary
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('fr-MG', {
            style: 'currency',
            currency: 'MGA',
            minimumFractionDigits: 0
        }).format(amount).replace('MGA', 'Ar');
    },
    
    // Format de nombre simple
    formatNumber: function(number) {
        return new Intl.NumberFormat('fr-FR').format(number);
    },
    
    // Formater une date
    formatDate: function(dateString, includeTime = false) {
        const date = new Date(dateString);
        const options = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        };
        
        if (includeTime) {
            options.hour = '2-digit';
            options.minute = '2-digit';
        }
        
        return date.toLocaleDateString('fr-FR', options);
    },
    
    // Afficher une notification toast
    showToast: function(message, type = 'info') {
        const toastContainer = this.getOrCreateToastContainer();
        const toastId = 'toast-' + Date.now();
        
        const toastHTML = `
            <div class="toast align-items-center text-bg-${type} border-0" role="alert" id="${toastId}">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Supprimer le toast après fermeture
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    },
    
    // Créer ou récupérer le conteneur de toasts
    getOrCreateToastContainer: function() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }
        return container;
    },
    
    // Confirmer une action de suppression
    confirmDelete: function(message = 'Êtes-vous sûr de vouloir supprimer cet élément ?') {
        return confirm(message);
    },
    
    // Valider un formulaire
    validateForm: function(formElement) {
        let isValid = true;
        const requiredFields = formElement.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    },
    
    // Activer la recherche en temps réel
    enableLiveSearch: function(searchInputId, targetTableId, searchColumns = [0]) {
        const searchInput = document.getElementById(searchInputId);
        const table = document.getElementById(targetTableId);
        
        if (!searchInput || !table) return;
        
        searchInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
            
            for (let i = 0; i < rows.length; i++) {
                let showRow = false;
                
                searchColumns.forEach(colIndex => {
                    const cell = rows[i].getElementsByTagName('td')[colIndex];
                    if (cell && cell.textContent.toLowerCase().includes(filter)) {
                        showRow = true;
                    }
                });
                
                rows[i].style.display = showRow ? '' : 'none';
            }
        });
    },
    
    // Calculateur automatique pour les formulaires de vente
    setupSalesCalculator: function(produitSelectId, quantiteInputId, totalDisplayId) {
        const produitSelect = document.getElementById(produitSelectId);
        const quantiteInput = document.getElementById(quantiteInputId);
        const totalDisplay = document.getElementById(totalDisplayId);
        
        if (!produitSelect || !quantiteInput || !totalDisplay) return;
        
        const calculateTotal = () => {
            const selectedOption = produitSelect.options[produitSelect.selectedIndex];
            if (!selectedOption) return;
            
            const prix = parseFloat(selectedOption.dataset.prix || 0);
            const quantite = parseInt(quantiteInput.value || 0);
            const total = prix * quantite;
            
            if (totalDisplay) {
                totalDisplay.textContent = this.formatCurrency(total);
            }
        };
        
        produitSelect.addEventListener('change', calculateTotal);
        quantiteInput.addEventListener('input', calculateTotal);
    },
    
    // Gestion des alertes de stock
    checkStockAlerts: function() {
        const stockElements = document.querySelectorAll('[data-stock-level]');
        
        stockElements.forEach(element => {
            const currentStock = parseInt(element.dataset.stockLevel);
            const threshold = parseInt(element.dataset.stockThreshold || 10);
            
            if (currentStock <= threshold) {
                element.classList.add('stock-alert');
                if (!element.querySelector('.stock-warning')) {
                    const warning = document.createElement('i');
                    warning.className = 'fas fa-exclamation-triangle text-warning stock-warning';
                    warning.title = 'Stock bas';
                    element.appendChild(warning);
                }
            }
        });
    }
};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Activer les tooltips Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Activer les popovers Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Vérifier les alertes de stock
    RuineGestion.checkStockAlerts();
    
    // Auto-fermeture des alertes après 5 secondes
    const alerts = document.querySelectorAll('.alert:not(.alert-no-dismiss)');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) bsAlert.close();
            }, 5000);
        }
    });
    
    // Formatage automatique des montants en Ariary
    const currencyElements = document.querySelectorAll('.currency-format');
    currencyElements.forEach(element => {
        if (element && element.textContent) {
            const amount = parseFloat(element.textContent);
            if (!isNaN(amount)) {
                element.textContent = RuineGestion.formatCurrency(amount);
            }
        }
    });
    
    // Confirmation automatique pour les boutons de suppression
    const deleteButtons = document.querySelectorAll('.btn-delete, .delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.dataset.confirmMessage || 'Êtes-vous sûr de vouloir supprimer cet élément ?';
            if (!RuineGestion.confirmDelete(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Validation en temps réel des formulaires
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!RuineGestion.validateForm(form)) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// Gestionnaire global pour les erreurs JavaScript
window.addEventListener('error', function(e) {
    console.error('Erreur JavaScript:', e.error);
    RuineGestion.showToast('Une erreur inattendue s\'est produite.', 'danger');
});

// Export pour utilisation modulaire
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RuineGestion;
}
