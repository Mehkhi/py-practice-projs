/**
 * Dashboard interactivity and animations
 */

(function() {
    'use strict';

    // Animate number count-up
    function animateValue(element, start, end, duration) {
        const range = end - start;
        const increment = range / (duration / 16); // 60fps
        let current = start;

        const timer = setInterval(function() {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 16);
    }

    // Initialize count-up animations for stat cards
    function initCountUpAnimations() {
        const statValues = document.querySelectorAll('.stat-card-value[data-target]');

        statValues.forEach(function(element) {
            const target = parseInt(element.getAttribute('data-target'), 10);
            if (target > 0) {
                // Use Intersection Observer to trigger animation when visible
                const observer = new IntersectionObserver(function(entries) {
                    entries.forEach(function(entry) {
                        if (entry.isIntersecting) {
                            animateValue(element, 0, target, 1000);
                            observer.unobserve(entry.target);
                        }
                    });
                }, { threshold: 0.5 });

                observer.observe(element);
            } else {
                element.textContent = '0';
            }
        });
    }

    // Animate progress ring
    function animateProgressRing() {
        const progressRing = document.querySelector('.progress-ring-fill');
        if (!progressRing) return;

        const total = parseInt(document.getElementById('today-total')?.textContent || '0', 10);
        const completed = parseInt(document.getElementById('today-completed')?.textContent || '0', 10);

        if (total === 0) return;

        const radius = progressRing.r?.baseVal?.value || 52;
        const circumference = radius * 2 * Math.PI;
        const offset = circumference - (completed / total) * circumference;

        // Set initial state
        progressRing.style.strokeDasharray = circumference;
        progressRing.style.strokeDashoffset = circumference;

        // Animate to target
        setTimeout(function() {
            progressRing.style.transition = 'stroke-dashoffset 1s ease-in-out';
            progressRing.style.strokeDashoffset = offset;
        }, 100);
    }

    // Add tooltips to activity calendar days
    function initActivityTooltips() {
        const activityDays = document.querySelectorAll('.activity-day');

        activityDays.forEach(function(day) {
            day.addEventListener('mouseenter', function(e) {
                const title = this.getAttribute('title');
                if (title) {
                    // Create tooltip
                    const tooltip = document.createElement('div');
                    tooltip.className = 'activity-tooltip';
                    tooltip.textContent = title;
                    tooltip.style.cssText = `
                        position: absolute;
                        background: var(--nord0);
                        color: var(--nord6);
                        padding: 8px 12px;
                        border-radius: 6px;
                        font-size: 0.875rem;
                        pointer-events: none;
                        z-index: 1000;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                        white-space: nowrap;
                    `;
                    document.body.appendChild(tooltip);

                    const rect = this.getBoundingClientRect();
                    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
                    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';

                    this._tooltip = tooltip;
                }
            });

            day.addEventListener('mouseleave', function() {
                if (this._tooltip) {
                    this._tooltip.remove();
                    this._tooltip = null;
                }
            });
        });
    }

    // Animate activity calendar on load
    function animateActivityCalendar() {
        const activityDays = document.querySelectorAll('.activity-day');

        activityDays.forEach(function(day, index) {
            day.style.opacity = '0';
            day.style.transform = 'translateY(20px)';

            setTimeout(function() {
                day.style.transition = 'all 0.3s ease';
                day.style.opacity = '1';
                day.style.transform = 'translateY(0)';
            }, index * 50);
        });
    }

    // Add pulse animation to streak card when streak > 0
    function animateStreakCard() {
        const streakCard = document.querySelector('[data-streak-card="true"]');
        const streakValue = parseInt(streakCard?.querySelector('.stat-card-value')?.getAttribute('data-target') || '0', 10);

        if (streakValue > 0) {
            streakCard?.classList.add('streak-active');
            streakCard.style.animation = 'pulse 2s ease-in-out infinite';
        }
    }

    // Add CSS animation for pulse
    function addPulseAnimation() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes pulse {
                0%, 100% {
                    transform: scale(1);
                }
                50% {
                    transform: scale(1.02);
                }
            }

            .streak-active {
                border-color: var(--nord12);
            }
        `;
        document.head.appendChild(style);
    }

    function animateBurndown() {
        const bars = document.querySelectorAll('.burndown-remaining');
        bars.forEach((bar) => {
            const targetHeight = bar.offsetHeight;
            bar.style.height = '0px';
            setTimeout(() => {
                bar.style.transition = 'height 0.5s ease';
                bar.style.height = `${targetHeight}px`;
            }, 60);
        });
    }

    // Initialize all animations when DOM is ready
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        addPulseAnimation();
        initCountUpAnimations();
        animateProgressRing();
        initActivityTooltips();
        animateActivityCalendar();
        animateStreakCard();
        animateBurndown();
    }

    // Start initialization
    init();
})();
