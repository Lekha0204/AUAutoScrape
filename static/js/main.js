/**
 * Main JavaScript file for Student Result Analysis System
 * Handles UI interactions, form validations, and progress tracking
 */


class StudentAnalysisApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupFormValidation();
    }

    setupEventListeners() {
        // Form choice toggle handlers
        const choiceRadios = document.querySelectorAll('input[name="choice"]');
        choiceRadios.forEach(radio => {
            radio.addEventListener('change', this.handleChoiceChange.bind(this));
        });

        // File upload handlers
        const fileInput = document.getElementById('dataFile');
        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        }

        // Form submission handlers
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        });

        // Drag and drop handlers
        this.setupDragAndDrop();

        // Keyboard accessibility
        this.setupKeyboardNavigation();
    }

    initializeComponents() {
        // Initialize tooltips
        this.initializeTooltips();
        
        // Initialize progress tracking if on results page
        if (window.location.pathname.includes('progress')) {
            this.initializeProgressTracking();
        }

        // Initialize charts if on analysis results page
        if (document.getElementById('gradeChart')) {
            this.initializeResultsPage();
        }
    }
    

    handleChoiceChange(event) {
        const choice = event.target.value;
        const singleInput = document.getElementById('singleInput');
        const rangeInput = document.getElementById('rangeInput');
        
        if (choice === 'single') {
            singleInput.style.display = 'block';
            rangeInput.style.display = 'none';
            this.toggleRequiredFields('single');
        } else if (choice === 'range') {
            singleInput.style.display = 'none';
            rangeInput.style.display = 'block';
            this.toggleRequiredFields('range');
        }
        
        // Add smooth transition effect
        this.animateFormChange();
    }

    toggleRequiredFields(type) {
        const singleField = document.getElementById('singleRollNo');
        const fromField = document.getElementById('fromRollNo');
        const toField = document.getElementById('toRollNo');

        if (type === 'single') {
            if (singleField) singleField.required = true;
            if (fromField) fromField.required = false;
            if (toField) toField.required = false;
        } else {
            if (singleField) singleField.required = false;
            if (fromField) fromField.required = true;
            if (toField) toField.required = true;
        }
    }

    animateFormChange() {
        const inputs = document.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.style.transition = 'all 0.3s ease';
        });
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file type
        const allowedTypes = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            'text/csv'
        ];

        if (!allowedTypes.includes(file.type)) {
            this.showAlert('Invalid file type. Please upload Excel or CSV files only.', 'error');
            event.target.value = '';
            return;
        }

        // Validate file size (16MB max)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showAlert('File too large. Maximum size is 16MB.', 'error');
            event.target.value = '';
            return;
        }

        this.updateFileInfo(file);
    }

    updateFileInfo(file) {
        const uploadPrompt = document.getElementById('uploadPrompt');
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');

        if (uploadPrompt && fileInfo && fileName && fileSize) {
            fileName.textContent = file.name;
            fileSize.textContent = this.formatFileSize(file.size);
            uploadPrompt.style.display = 'none';
            fileInfo.style.display = 'block';

            // Update file icon based on type
            const icon = fileInfo.querySelector('i');
            if (icon) {
                if (file.name.endsWith('.csv')) {
                    icon.className = 'fas fa-file-csv fa-2x text-success me-3';
                } else {
                    icon.className = 'fas fa-file-excel fa-2x text-success me-3';
                }
            }

            // Add animation
            fileInfo.style.opacity = '0';
            fileInfo.style.transform = 'translateY(10px)';
            setTimeout(() => {
                fileInfo.style.transition = 'all 0.3s ease';
                fileInfo.style.opacity = '1';
                fileInfo.style.transform = 'translateY(0)';
            }, 10);
        }
    }




    setupDragAndDrop() {
        const uploadArea = document.getElementById('fileUploadArea');
        if (!uploadArea) return;

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const fileInput = document.getElementById('dataFile');
                if (fileInput) {
                    fileInput.files = files;
                    this.handleFileSelect({ target: fileInput });
                }
            }
        });

        // Click to upload
        uploadArea.addEventListener('click', (e) => {
            if (e.target === uploadArea || e.target.closest('#uploadPrompt')) {
                const fileInput = document.getElementById('dataFile');
                if (fileInput) fileInput.click();
            }
        });
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    return false;
                }
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });

        // Validate roll number format
        const rollNoFields = form.querySelectorAll('input[name="single"], input[name="from"], input[name="to"]');
        rollNoFields.forEach(field => {
            if (field.value && field.required) {
                if (!this.validateRollNumber(field.value)) {
                    this.showFieldError(field, 'Invalid roll number format');
                    isValid = false;
                }
            }
        });

        // Validate range
        const fromField = form.querySelector('input[name="from"]');
        const toField = form.querySelector('input[name="to"]');


        return isValid;
    }

    validateRollNumber(rollNo) {
        // Basic roll number validation - adjust pattern as needed
        const pattern = /^[0-9]{2}[A-Za-z]{2}[0-9]{3}[A-Za-z]{1}[0-9]{2}$/;
        return pattern.test(rollNo);
    }

    validateRollNumberRange(from, to) {
        try {
            const fromNum = parseInt(from.slice(-3));
            const toNum = parseInt(to.slice(-3));
            const fromPrefix = from.slice(0, -3);
            const toPrefix = to.slice(0, -3);
            
            return fromPrefix === toPrefix && fromNum <= toNum;
        } catch (e) {
            return false;
        }
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        field.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    handleFormSubmit(event) {
    const form = event.target;

    // Prevent multiple submissions
    if (form.classList.contains('submitted')) {
        event.preventDefault();
        return false;
    }

    form.classList.add('submitted');

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        const originalHTML = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        submitBtn.disabled = true;

        // Re-enable button and form flag after 30 seconds (fallback)
        setTimeout(() => {
            form.classList.remove('submitted');
            submitBtn.innerHTML = originalHTML;
            submitBtn.disabled = false;
        }, 30000);
    }
}

    initializeTooltips() {
        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    setupKeyboardNavigation() {
        // Add keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl+Enter to submit forms
            if (e.ctrlKey && e.key === 'Enter') {
                const activeForm = document.activeElement.closest('form');
                if (activeForm) {
                    activeForm.requestSubmit();
                }
            }
            
            // Escape to close modals or reset forms
            if (e.key === 'Escape') {
                this.handleEscape();
            }
        });
    }

    handleEscape() {
        // Close any open modals
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }

    showAlert(message, type = 'info') {
        // Create and show alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert alert at top of main content
        const main = document.querySelector('main');
        if (main) {
            main.insertBefore(alertDiv, main.firstChild);
            
            // Auto dismiss after 5 seconds
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Utility method to create loading overlay
    showLoadingOverlay(message = 'Processing...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'loadingOverlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin fa-3x mb-3"></i>
                <h4>${message}</h4>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.remove();
        }
    }

    // Method to handle progressive enhancement
    enhanceProgressively() {
        // Add classes for CSS animations
        document.body.classList.add('js-enabled');
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const app = new StudentAnalysisApp();
    
    // Make clearFile function globally available
    window.clearFile = app.clearFile.bind(app);
    
    // Progressive enhancement
    app.enhanceProgressively();
    
    console.log('Student Analysis App initialized successfully');
});

// Export for use in other modules
window.StudentAnalysisApp = StudentAnalysisApp;
