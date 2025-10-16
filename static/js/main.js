// Main JavaScript file for CRWV Moon application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap tooltips are used
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add loading state to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                submitBtn.disabled = true;
                
                // Re-enable button after 10 seconds as fallback
                setTimeout(function() {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                    feather.replace();
                }, 10000);
            }
        });
    });

    // Enhanced phone number formatting
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
        
        input.addEventListener('paste', function(e) {
            setTimeout(() => formatPhoneNumber(this), 0);
        });
    });

    // Real-time validation for phone numbers
    phoneInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validatePhoneNumber(this);
        });
    });
});

// Phone number formatting function
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    
    // Ensure US country code
    if (value.length > 0 && !value.startsWith('1')) {
        value = '1' + value;
    }
    
    // Limit to reasonable length
    if (value.length > 11) {
        value = value.slice(0, 11);
    }
    
    // Add plus sign
    if (value.length > 0) {
        input.value = '+' + value;
    } else {
        input.value = '';
    }
}

// Phone number validation
function validatePhoneNumber(input) {
    const phoneRegex = /^\+1\d{10}$/;
    const isValid = !input.value || phoneRegex.test(input.value);
    
    if (isValid) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        
        // Remove any existing error message
        const existingFeedback = input.parentNode.querySelector('.invalid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        
        // Add error message if not exists
        let feedback = input.parentNode.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            input.parentNode.appendChild(feedback);
        }
        feedback.textContent = 'Please enter a valid US phone number (+1XXXXXXXXXX)';
    }
}

// Utility function to show loading state on any button
function setButtonLoading(button, loadingText = 'Loading...') {
    if (button.dataset.originalText) return; // Already loading
    
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${loadingText}`;
    button.disabled = true;
}

// Utility function to restore button from loading state
function resetButtonLoading(button) {
    if (!button.dataset.originalText) return; // Not in loading state
    
    button.innerHTML = button.dataset.originalText;
    button.disabled = false;
    delete button.dataset.originalText;
    
    // Re-initialize feather icons
    feather.replace();
}

// API call helper with error handling
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Show notification/toast message
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'danger' ? 'alert-circle' : 'info';
    
    alertDiv.innerHTML = `
        <i data-feather="${icon}" class="me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of main container
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        feather.replace();
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}

// Format currency helper
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

// Format large numbers with commas
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

// Get time ago string
function timeAgo(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'just now';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    }
}

// Copy to clipboard function
function copyToClipboard(text, button = null) {
    navigator.clipboard.writeText(text).then(() => {
        if (button) {
            const originalText = button.innerHTML;
            button.innerHTML = '<i data-feather="check" class="me-1"></i>Copied!';
            button.classList.add('btn-success');
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.classList.remove('btn-success');
                feather.replace();
            }, 2000);
        }
        showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy to clipboard', 'danger');
    });
}

// Refresh stock price function
async function refreshPrice() {
    const priceElement = document.querySelector('h2.text-success, h2.text-warning');
    const changeElements = document.querySelectorAll('.badge.fs-6');
    const lastUpdatedElement = document.getElementById('last-updated');
    
    if (!priceElement || !lastUpdatedElement) return;
    
    try {
        // Show loading state
        priceElement.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
        priceElement.className = 'text-info';
        
        // Fetch new data
        const data = await apiCall('/api/stock-data');
        
        if (data.success && data.current_price) {
            // Update price
            priceElement.innerHTML = `$${data.current_price.toFixed(2)}`;
            priceElement.className = 'text-success';
            
            // Update daily percentage change (first badge)
            if (changeElements[0] && data.daily_change_percent !== null) {
                const isPositive = data.daily_change_percent >= 0;
                changeElements[0].className = `badge fs-6 ${isPositive ? 'bg-success' : 'bg-danger'}`;
                changeElements[0].innerHTML = `
                    <i data-feather="${isPositive ? 'trending-up' : 'trending-down'}" class="me-1"></i>
                    ${isPositive ? '+' : ''}${data.daily_change_percent.toFixed(2)}%
                `;
            }
            
            // Update weekly percentage change (second badge)
            if (changeElements[1] && data.weekly_change_percent !== null) {
                const isPositive = data.weekly_change_percent >= 0;
                changeElements[1].className = `badge fs-6 ${isPositive ? 'bg-success' : 'bg-danger'}`;
                changeElements[1].style.opacity = '0.8';
                changeElements[1].innerHTML = `
                    <i data-feather="${isPositive ? 'trending-up' : 'trending-down'}" class="me-1"></i>
                    ${isPositive ? '+' : ''}${data.weekly_change_percent.toFixed(2)}% (7d)
                `;
            }
            
            // Re-initialize feather icons
            feather.replace();
            
            // Update last updated time
            lastUpdatedElement.textContent = 'Just now';
            
            showNotification('Price updated successfully!', 'success');
        } else {
            // Show error state
            priceElement.innerHTML = 'Unavailable';
            priceElement.className = 'text-warning';
            showNotification('Failed to fetch price data', 'danger');
        }
    } catch (error) {
        console.error('Error refreshing price:', error);
        priceElement.innerHTML = 'Unavailable';
        priceElement.className = 'text-warning';
        showNotification('Error fetching price data', 'danger');
    }
}

// Export functions for global use
window.CRWVMoon = {
    setButtonLoading,
    resetButtonLoading,
    apiCall,
    showNotification,
    formatCurrency,
    formatNumber,
    timeAgo,
    copyToClipboard,
    formatPhoneNumber,
    validatePhoneNumber,
    refreshPrice
};

// Make refreshPrice globally available
window.refreshPrice = refreshPrice;
