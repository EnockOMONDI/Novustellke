/* Promotional Popup Admin JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Add visual enhancements to the admin interface
    
    // Enhance the image preview field
    const imagePreview = document.querySelector('.field-image_preview img');
    if (imagePreview) {
        imagePreview.addEventListener('click', function() {
            // Open image in a modal or new tab for better viewing
            window.open(this.src, '_blank');
        });
        
        // Add tooltip
        imagePreview.title = 'Click to view full size';
        imagePreview.style.cursor = 'pointer';
    }
    
    // Add real-time validation for display order
    const displayOrderField = document.querySelector('.field-display_order input');
    if (displayOrderField) {
        displayOrderField.addEventListener('input', function() {
            const value = parseInt(this.value);
            if (value < 1) {
                this.style.borderColor = '#dc3545';
                this.title = 'Display order must be 1 or higher';
            } else {
                this.style.borderColor = '#28a745';
                this.title = 'Valid display order';
            }
        });
    }
    
    // Add confirmation for bulk actions
    const actionSelect = document.querySelector('.actions select');
    const actionButton = document.querySelector('.actions button[type="submit"]');
    
    if (actionSelect && actionButton) {
        actionButton.addEventListener('click', function(e) {
            const selectedAction = actionSelect.value;
            const selectedItems = document.querySelectorAll('input[name="_selected_action"]:checked');
            
            if (selectedItems.length === 0) {
                e.preventDefault();
                alert('Please select at least one popup to perform this action.');
                return;
            }
            
            let confirmMessage = '';
            switch (selectedAction) {
                case 'delete_selected':
                    confirmMessage = `Are you sure you want to delete ${selectedItems.length} popup(s)?`;
                    break;
                case 'activate_popups':
                    confirmMessage = `Activate ${selectedItems.length} popup(s)?`;
                    break;
                case 'deactivate_popups':
                    confirmMessage = `Deactivate ${selectedItems.length} popup(s)?`;
                    break;
                case 'reset_statistics':
                    confirmMessage = `Reset statistics for ${selectedItems.length} popup(s)? This action cannot be undone.`;
                    break;
            }
            
            if (confirmMessage && !confirm(confirmMessage)) {
                e.preventDefault();
            }
        });
    }
    
    // Add visual indicators for active/inactive status
    const statusCells = document.querySelectorAll('.field-is_active');
    statusCells.forEach(function(cell) {
        const checkbox = cell.querySelector('input[type="checkbox"]');
        if (checkbox) {
            const indicator = document.createElement('span');
            indicator.className = 'status-indicator';
            indicator.style.cssText = `
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-left: 8px;
                background-color: ${checkbox.checked ? '#28a745' : '#dc3545'};
            `;
            cell.appendChild(indicator);
            
            checkbox.addEventListener('change', function() {
                indicator.style.backgroundColor = this.checked ? '#28a745' : '#dc3545';
            });
        }
    });
    
    // Add click-through rate color coding
    const ctrCells = document.querySelectorAll('.field-click_through_rate_display');
    ctrCells.forEach(function(cell) {
        const text = cell.textContent.trim();
        const rate = parseFloat(text);
        
        if (!isNaN(rate)) {
            if (rate === 0) {
                cell.style.color = '#6c757d';
            } else if (rate < 1) {
                cell.style.color = '#dc3545';
            } else if (rate < 3) {
                cell.style.color = '#fd7e14';
            } else {
                cell.style.color = '#28a745';
            }
        }
    });
    
    // Add tooltips for statistics
    const viewCountCells = document.querySelectorAll('.field-view_count');
    viewCountCells.forEach(function(cell) {
        const count = parseInt(cell.textContent.trim());
        if (!isNaN(count)) {
            cell.title = `This popup has been viewed ${count} time(s)`;
        }
    });
    
    const clickCountCells = document.querySelectorAll('.field-click_count');
    clickCountCells.forEach(function(cell) {
        const count = parseInt(cell.textContent.trim());
        if (!isNaN(count)) {
            cell.title = `The inquiry button has been clicked ${count} time(s)`;
        }
    });
});

// Add custom styling for better UX
const style = document.createElement('style');
style.textContent = `
    .status-indicator {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .field-click_through_rate_display {
        font-weight: bold;
        transition: color 0.3s ease;
    }
    
    .actions {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }
`;
document.head.appendChild(style);
