// KaamSet - Main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Image preview for file upload
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('image-preview-container');
    
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                
                // Check file size
                const maxSize = 16 * 1024 * 1024; // 16MB
                if (file.size > maxSize) {
                    showAlert('File size exceeds 16MB. Please choose a smaller file.', 'danger');
                    this.value = '';
                    return;
                }
                
                // Check file type
                const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/svg+xml'];
                if (!validTypes.includes(file.type)) {
                    showAlert('Invalid file type. Please upload an image file.', 'danger');
                    this.value = '';
                    return;
                }
                
                // Show image preview if container exists
                if (imagePreview) {
                    reader.onload = function(e) {
                        // Create preview if it doesn't exist yet
                        if (!document.getElementById('image-preview')) {
                            const img = document.createElement('img');
                            img.id = 'image-preview';
                            img.className = 'img-thumbnail mt-2';
                            img.style.maxHeight = '200px';
                            imagePreview.appendChild(img);
                        }
                        
                        // Update preview image
                        const preview = document.getElementById('image-preview');
                        preview.src = e.target.result;
                        imagePreview.classList.remove('d-none');
                    }
                    reader.readAsDataURL(file);
                }
            }
        });
    }

    // Handle skill filter change
    const skillFilter = document.getElementById('skill-filter');
    if (skillFilter) {
        skillFilter.addEventListener('change', function() {
            this.form.submit();
        });
    }
    
    // Form reset functionality
    const registrationForm = document.getElementById('worker-registration-form');
    const resetButton = document.getElementById('reset-form');
    
    if (resetButton && registrationForm) {
        resetButton.addEventListener('click', function(e) {
            e.preventDefault();
            registrationForm.reset();
            
            // Clear any validation classes
            const inputs = registrationForm.querySelectorAll('.form-control, .form-select');
            inputs.forEach(input => {
                input.classList.remove('is-invalid', 'is-valid');
            });
            
            registrationForm.classList.remove('was-validated');
            
            // Clear image preview if it exists
            if (imagePreview) {
                imagePreview.innerHTML = '';
                imagePreview.classList.add('d-none');
            }
            
            // Scroll to top of form
            registrationForm.scrollIntoView({ behavior: 'smooth' });
            
            showAlert('Form has been reset.', 'info');
        });
    }
    
    // Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
    
    // Helper function to show bootstrap alerts
    function showAlert(message, type) {
        const alertPlaceholder = document.getElementById('alert-container');
        if (!alertPlaceholder) return;
        
        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        alertPlaceholder.appendChild(wrapper);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            const alert = wrapper.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
});
