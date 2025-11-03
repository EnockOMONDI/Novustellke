/* Novustell Travel - Custom Unfold Admin JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize custom functionality
    initializeNovustellAdmin();
    
    // Add travel-themed enhancements
    enhanceTravelInterface();
    
    // Initialize form enhancements
    enhanceForms();
    
    // Add responsive behavior
    handleResponsiveNavigation();

    // Enhance admin actions
    enhanceAdminActions();
});

function initializeNovustellAdmin() {
    console.log('Novustell Travel Admin Interface Initialized');
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Add slide-in animation to sidebar
    const sidebar = document.querySelector('.unfold-sidebar');
    if (sidebar) {
        sidebar.classList.add('slide-in-left');
    }
}

function enhanceTravelInterface() {
    // Add travel-themed icons to navigation items
    const navItems = {
        'Destinations': 'fas fa-map-marker-alt',
        'Packages': 'fas fa-suitcase-rolling',
        'Accommodations': 'fas fa-hotel',
        'Travel Modes': 'fas fa-plane',
        'Blog Posts': 'fas fa-blog',
        'Categories': 'fas fa-tags'
    };
    
    Object.entries(navItems).forEach(([text, iconClass]) => {
        const navLink = Array.from(document.querySelectorAll('.nav-link')).find(
            link => link.textContent.trim().includes(text)
        );
        
        if (navLink && !navLink.querySelector('i')) {
            const icon = document.createElement('i');
            icon.className = `${iconClass} travel-icon me-2`;
            navLink.insertBefore(icon, navLink.firstChild);
        }
    });
    
    // Add status indicators for packages
    enhancePackageStatus();
    
    // Add destination type indicators
    enhanceDestinationTypes();
}

function enhancePackageStatus() {
    const statusElements = document.querySelectorAll('[data-status]');
    statusElements.forEach(element => {
        const status = element.getAttribute('data-status');
        element.classList.add(`package-status-${status.toLowerCase()}`);
    });
}

function enhanceDestinationTypes() {
    const typeElements = document.querySelectorAll('[data-destination-type]');
    typeElements.forEach(element => {
        const type = element.getAttribute('data-destination-type');
        element.classList.add(`destination-type-${type.toLowerCase()}`);
    });
}

function enhanceForms() {
    // Skip form enhancements for Django admin pages
    if (window.location.pathname.includes('/admin/')) {
        console.log('Skipping form enhancements for Django admin');
        return;
    }

    // Add enhanced styling to form fields
    const formFields = document.querySelectorAll('.form-control, .form-select');
    formFields.forEach(field => {
        const wrapper = field.closest('.field-wrapper') || field.parentElement;

        // Add focus enhancement
        field.addEventListener('focus', function() {
            wrapper.classList.add('field-focused');
        });

        field.addEventListener('blur', function() {
            wrapper.classList.remove('field-focused');
        });
    });

    // Enhance image upload fields
    enhanceImageUploads();

    // Add form validation enhancements
    enhanceFormValidation();
}

function enhanceImageUploads() {
    const imageInputs = document.querySelectorAll('input[type="file"]');
    imageInputs.forEach(input => {
        if (input.accept && input.accept.includes('image')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'image-upload-wrapper';
            
            const label = document.createElement('label');
            label.innerHTML = `
                <i class="fas fa-cloud-upload-alt fa-2x mb-2 d-block"></i>
                <span>Click to upload image or drag and drop</span>
            `;
            label.appendChild(input.cloneNode(true));
            
            wrapper.appendChild(label);
            input.parentNode.replaceChild(wrapper, input);
            
            // Add drag and drop functionality
            addDragDropToImageUpload(wrapper);
        }
    });
}

function addDragDropToImageUpload(wrapper) {
    const input = wrapper.querySelector('input[type="file"]');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        wrapper.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        wrapper.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        wrapper.addEventListener(eventName, unhighlight, false);
    });
    
    wrapper.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        wrapper.classList.add('drag-over');
    }
    
    function unhighlight() {
        wrapper.classList.remove('drag-over');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            input.files = files;
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
}

function enhanceFormValidation() {
    // Only apply custom validation to non-admin forms
    const forms = document.querySelectorAll('form:not([action*="/admin/"])');
    forms.forEach(form => {
        // Skip Django admin forms to prevent interference
        if (form.closest('.admin') || form.querySelector('.django-ckeditor-5')) {
            return;
        }

        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                // Skip CKEditor5 fields as they have their own validation
                if (field.classList.contains('django-ckeditor-5') ||
                    field.closest('.ck-editor')) {
                    return;
                }

                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();
                showValidationMessage('Please fill in all required fields.');
            }
        });
    });
}

function handleResponsiveNavigation() {
    const toggleBtn = document.querySelector('.navbar-toggler');
    const sidebar = document.querySelector('.unfold-sidebar');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768 &&
                !sidebar.contains(e.target) &&
                !toggleBtn.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        });
    }
}

function enhanceAdminActions() {
    // Only run on admin pages
    if (!window.location.pathname.includes('/admin/')) {
        return;
    }

    console.log('🔧 Enhancing admin actions...');

    // Try multiple selectors to find the actions container
    const actionsContainer = document.querySelector('.actions') ||
                            document.querySelector('.changelist-actions') ||
                            document.querySelector('.admin-actions') ||
                            document.querySelector('[class*="action"]');

    // Try multiple selectors for action select
    const actionSelect = document.querySelector('select[name="action"]') ||
                        document.querySelector('.actions select') ||
                        document.querySelector('.changelist-actions select');

    // Try multiple selectors for submit button
    const submitButton = document.querySelector('button[name="index"]') ||
                        document.querySelector('input[name="index"]') ||
                        document.querySelector('.actions button[type="submit"]') ||
                        document.querySelector('.actions input[type="submit"]') ||
                        document.querySelector('.changelist-actions button[type="submit"]') ||
                        document.querySelector('.changelist-actions input[type="submit"]');

    const checkboxes = document.querySelectorAll('input[name="_selected_action"]');

    console.log('🔍 Found elements:', {
        actionsContainer: !!actionsContainer,
        actionSelect: !!actionSelect,
        submitButton: !!submitButton,
        checkboxes: checkboxes.length
    });

    if (!actionsContainer || !actionSelect || !submitButton) {
        console.warn('⚠️ Could not find all required admin action elements');

        // Force create a visible button if one doesn't exist
        if (actionSelect && !submitButton) {
            const newButton = document.createElement('button');
            newButton.type = 'submit';
            newButton.name = 'index';
            newButton.value = '0';
            newButton.textContent = 'GO';
            newButton.className = 'btn-submit novustell-go-button';

            // Insert after the select element
            actionSelect.parentNode.insertBefore(newButton, actionSelect.nextSibling);
            console.log('✅ Created missing GO button');
        }

        return;
    }

    // Force the button to be visible
    submitButton.style.display = 'inline-block';
    submitButton.style.visibility = 'visible';
    submitButton.style.opacity = '1';

    // Add our custom class for styling
    submitButton.classList.add('novustell-go-button');

    console.log('✅ Admin actions enhancement applied');

    // Function to update action button state
    function updateActionButton() {
        const selectedAction = actionSelect.value;
        const selectedItems = Array.from(checkboxes).filter(cb => cb.checked).length;

        console.log('🔄 Updating button state:', { selectedAction, selectedItems });

        if (selectedAction && selectedAction !== '---------' && selectedItems > 0) {
            submitButton.style.display = 'inline-block';
            submitButton.textContent = `Execute Action (${selectedItems} selected)`;
            if (actionsContainer) {
                actionsContainer.classList.add('has-selection');
            }

            // Add action counter
            let counter = actionsContainer ? actionsContainer.querySelector('.action-counter') : null;
            if (!counter && actionsContainer) {
                counter = document.createElement('span');
                counter.className = 'action-counter';
                submitButton.parentNode.insertBefore(counter, submitButton.nextSibling);
            }
            if (counter) {
                counter.textContent = `${selectedItems} item${selectedItems !== 1 ? 's' : ''}`;
            }
        } else {
            submitButton.style.display = 'inline-block'; // Always keep visible
            submitButton.textContent = 'GO';
            if (actionsContainer) {
                actionsContainer.classList.remove('has-selection');
            }

            const counter = actionsContainer ? actionsContainer.querySelector('.action-counter') : null;
            if (counter) {
                counter.remove();
            }
        }

        // Force visibility
        submitButton.style.visibility = 'visible';
        submitButton.style.opacity = '1';
    }

    // Listen for action selection changes
    actionSelect.addEventListener('change', updateActionButton);

    // Listen for checkbox changes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateActionButton);
    });

    // Listen for "select all" checkbox
    const selectAllCheckbox = document.querySelector('#action-toggle') ||
                             document.querySelector('input[type="checkbox"][onclick*="toggle"]');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            setTimeout(updateActionButton, 10); // Small delay to ensure checkboxes are updated
        });
    }

    // Initial state
    updateActionButton();

    // Add confirmation for destructive actions
    submitButton.addEventListener('click', function(e) {
        const selectedAction = actionSelect.value;
        const selectedItems = Array.from(checkboxes).filter(cb => cb.checked).length;

        console.log('🖱️ Button clicked:', { selectedAction, selectedItems });

        if (selectedItems === 0) {
            e.preventDefault();
            alert('Please select at least one item to perform this action.');
            return;
        }

        // Add confirmation for potentially destructive actions
        const destructiveActions = ['delete_selected', 'cancel_campaign', 'mark_unsubscribed'];
        if (destructiveActions.some(action => selectedAction.includes(action))) {
            const actionText = actionSelect.options[actionSelect.selectedIndex].text;
            if (!confirm(`Are you sure you want to ${actionText.toLowerCase()} ${selectedItems} item${selectedItems !== 1 ? 's' : ''}?`)) {
                e.preventDefault();
                return;
            }
        }

        // Add loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="loading-spinner"></span> Processing...';

        // Re-enable after a delay (in case of errors)
        setTimeout(() => {
            submitButton.disabled = false;
            updateActionButton();
        }, 5000);
    });

    // Add a visual indicator that the enhancement is active
    if (actionsContainer) {
        actionsContainer.setAttribute('data-novustell-enhanced', 'true');
    }
}

function showValidationMessage(message) {
    // Create or update validation message
    let messageEl = document.querySelector('.validation-message');
    if (!messageEl) {
        messageEl = document.createElement('div');
        messageEl.className = 'alert alert-error validation-message';
        document.querySelector('form').insertBefore(messageEl, document.querySelector('form').firstChild);
    }
    
    messageEl.textContent = message;
    messageEl.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 5000);
}

function showSuccessMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.className = 'alert alert-success';
    messageEl.textContent = message;
    
    document.body.insertBefore(messageEl, document.body.firstChild);
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        messageEl.remove();
    }, 3000);
}

// Utility functions for admin interface
window.NovustellAdmin = {
    showLoading: function(element) {
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        element.appendChild(spinner);
    },
    
    hideLoading: function(element) {
        const spinner = element.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    },
    
    showSuccess: showSuccessMessage,
    
    showError: function(message) {
        showValidationMessage(message);
    }
};

// Initialize tooltips and popovers if Bootstrap is available
if (typeof bootstrap !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    });
}
