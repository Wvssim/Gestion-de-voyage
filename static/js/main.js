// Travel Booking Platform - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add active class to current link in navbar
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath && currentLocation === linkPath) {
            link.classList.add('active');
        }
    });

    // Seat number input validation for booking
    const seatInput = document.getElementById('id_num_seats');
    if (seatInput) {
        seatInput.addEventListener('change', function() {
            const maxSeats = parseInt(this.getAttribute('max')) || 1;
            const value = parseInt(this.value) || 0;
            
            if (value < 1) {
                this.value = 1;
            } else if (value > maxSeats) {
                this.value = maxSeats;
                showAlert('Only ' + maxSeats + ' seats available.', 'warning');
            }
            
            // If there's a price calculator function, trigger it
            if (typeof updateTotalPrice === 'function') {
                updateTotalPrice();
            }
        });
    }

    // Travel filter form - auto-submit on change for select fields
    const filterForm = document.querySelector('form[id="filter-form"]');
    if (filterForm) {
        const selects = filterForm.querySelectorAll('select');
        selects.forEach(select => {
            select.addEventListener('change', function() {
                filterForm.submit();
            });
        });
    }

    // Initialize date pickers with default format
    const datePickers = document.querySelectorAll('input[type="date"]');
    datePickers.forEach(picker => {
        // Add min date attribute to prevent selecting dates in the past for travel dates
        if (picker.id === 'id_start_date' || picker.id === 'id_end_date') {
            const today = new Date().toISOString().split('T')[0];
            picker.setAttribute('min', today);
        }
    });

    // Confirmation popups for delete/cancel actions
    const confirmActions = document.querySelectorAll('[data-confirm]');
    confirmActions.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Function to show custom alerts
    window.showAlert = function(message, type = 'info') {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
        alertContainer.setAttribute('role', 'alert');
        
        alertContainer.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertContainer, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertContainer);
            bsAlert.close();
        }, 5000);
    };

    // Simple counter animation for dashboard stats
    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
        const target = parseInt(counter.innerText);
        let count = 0;
        const speed = Math.max(10, Math.floor(target / 20)); // Adjust animation speed based on number size
        
        const updateCount = () => {
            const increment = Math.ceil(target / (1000 / speed));
            if (count < target) {
                count = Math.min(count + increment, target);
                counter.innerText = count;
                setTimeout(updateCount, speed);
            } else {
                counter.innerText = target;
            }
        };
        
        updateCount();
    });
});
