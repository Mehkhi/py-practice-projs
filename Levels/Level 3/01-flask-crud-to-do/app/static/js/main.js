// Simple JavaScript for enhanced user interactions
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling for anchor links using event delegation
    document.addEventListener('click', function(e) {
        if (e.target.matches('a[href^="#"]')) {
            e.preventDefault();
            const target = document.querySelector(e.target.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        }
    });

    // Add loading state to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.textContent;
                submitBtn.disabled = true;
                submitBtn.textContent = 'Loading...';

                // Store original text for cleanup
                submitBtn.dataset.originalText = originalText;

                // Re-enable after 5 seconds as a fallback
                const timeoutId = setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }, 5000);

                // Store timeout ID for potential cleanup
                submitBtn.dataset.timeoutId = timeoutId;
            }
        });
    });

    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        const timeoutId = setTimeout(() => {
            message.style.transition = 'opacity 0.3s, transform 0.3s';
            message.style.opacity = '0';
            message.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);

        // Store timeout ID for potential cleanup
        message.dataset.timeoutId = timeoutId;
    });

    // Add confirmation for delete actions with better UX - using event delegation
    document.addEventListener('submit', function(e) {
        if (e.target.matches('form[onsubmit*="confirm"]')) {
            const taskTitle = e.target.closest('.task-item')?.querySelector('.task-title')?.textContent;
            const confirmMessage = taskTitle
                ? `Are you sure you want to delete "${taskTitle}"?`
                : 'Are you sure you want to delete this task?';

            if (!confirm(confirmMessage)) {
                e.preventDefault();
            }
        }
    });
});

// Cleanup function for page unload
window.addEventListener('beforeunload', function() {
    // Clear any pending timeouts
    document.querySelectorAll('[data-timeout-id]').forEach(element => {
        const timeoutId = element.dataset.timeoutId;
        if (timeoutId) {
            clearTimeout(parseInt(timeoutId));
        }
    });
});
