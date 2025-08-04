// Minecraft Bedwars Leaderboard - Main JavaScript
// Enhanced interactivity and gaming experience

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Update current time
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize form enhancements
    initializeFormEnhancements();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize mobile optimizations
    initializeMobileOptimizations();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Initialize performance monitoring
    initializePerformanceMonitoring();
    
    console.log('🎮 Bedwars Leaderboard initialized successfully!');
}

// Time Management
function updateCurrentTime() {
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        const now = new Date();
        const options = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        };
        timeElement.textContent = now.toLocaleString('ru-RU', options);
    }
}

// Tooltip System
function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add custom tooltips for stats
    addStatTooltips();
}

function addStatTooltips() {
    // K/D Ratio tooltips
    document.querySelectorAll('.stat-value').forEach(element => {
        if (element.textContent.includes('.')) {
            const ratio = parseFloat(element.textContent);
            let tooltip = '';
            if (ratio >= 2.0) tooltip = 'Превосходно! 🏆';
            else if (ratio >= 1.5) tooltip = 'Отлично! ⭐';
            else if (ratio >= 1.0) tooltip = 'Хорошо! 👍';
            else tooltip = 'Есть куда расти! 💪';
            
            element.setAttribute('title', tooltip);
            element.setAttribute('data-bs-toggle', 'tooltip');
        }
    });
    
    // Level tooltips
    document.querySelectorAll('.level-badge').forEach(element => {
        const level = parseInt(element.textContent);
        let tooltip = '';
        if (level >= 50) tooltip = 'Легендарный игрок! 🌟';
        else if (level >= 25) tooltip = 'Опытный воин! ⚔️';
        else if (level >= 10) tooltip = 'Продвинутый игрок! 🎯';
        else tooltip = 'Начинающий игрок 🌱';
        
        element.setAttribute('title', tooltip);
        element.setAttribute('data-bs-toggle', 'tooltip');
    });
}

// Animation System
function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.stat-card, .player-row, .chart-card').forEach(el => {
        observer.observe(el);
    });
    
    // Add stagger animation to table rows
    animateTableRows();
    
    // Add hover effects
    addHoverEffects();
}

function animateTableRows() {
    const rows = document.querySelectorAll('.player-row');
    rows.forEach((row, index) => {
        setTimeout(() => {
            row.style.opacity = '0';
            row.style.transform = 'translateX(-20px)';
            row.style.transition = 'all 0.5s ease';
            
            setTimeout(() => {
                row.style.opacity = '1';
                row.style.transform = 'translateX(0)';
            }, 50);
        }, index * 50);
    });
}

function addHoverEffects() {
    // Enhanced table row hover
    document.querySelectorAll('.player-row').forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
            this.style.boxShadow = 'inset 4px 0 0 var(--warning-color)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
            this.style.boxShadow = '';
        });
    });
    
    // Card hover effects
    document.querySelectorAll('.stat-card, .admin-stat-card, .action-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Form Enhancements
function initializeFormEnhancements() {
    // Real-time form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        addFormValidation(form);
    });
    
    // Auto-calculate stats
    initializeStatCalculators();
    
    // Form auto-save for admin panel
    initializeAutoSave();
}

function addFormValidation(form) {
    const inputs = form.querySelectorAll('input[type="number"]');
    
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            validateNumberInput(this);
        });
        
        input.addEventListener('blur', function() {
            formatNumberInput(this);
        });
    });
    
    // Nickname validation
    const nicknameInput = form.querySelector('input[name="nickname"]');
    if (nicknameInput) {
        nicknameInput.addEventListener('input', function() {
            validateNickname(this);
        });
    }
}

function validateNumberInput(input) {
    const value = parseInt(input.value);
    const min = parseInt(input.getAttribute('min')) || 0;
    const max = parseInt(input.getAttribute('max')) || 999999;
    
    input.classList.remove('is-valid', 'is-invalid');
    
    if (isNaN(value) || value < min || value > max) {
        input.classList.add('is-invalid');
        showFieldError(input, `Значение должно быть от ${min} до ${max}`);
    } else {
        input.classList.add('is-valid');
        clearFieldError(input);
    }
}

function validateNickname(input) {
    const value = input.value.trim();
    const minLength = 1;
    const maxLength = 20;
    
    input.classList.remove('is-valid', 'is-invalid');
    
    if (value.length < minLength || value.length > maxLength) {
        input.classList.add('is-invalid');
        showFieldError(input, `Ник должен содержать от ${minLength} до ${maxLength} символов`);
    } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
        input.classList.add('is-invalid');
        showFieldError(input, 'Ник может содержать только буквы, цифры и подчеркивания');
    } else {
        input.classList.add('is-valid');
        clearFieldError(input);
    }
}

function showFieldError(input, message) {
    clearFieldError(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    errorDiv.dataset.fieldError = 'true';
    
    input.parentNode.appendChild(errorDiv);
}

function clearFieldError(input) {
    const errorDiv = input.parentNode.querySelector('[data-field-error="true"]');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function formatNumberInput(input) {
    if (input.value && !isNaN(input.value)) {
        input.value = parseInt(input.value).toString();
    }
}

function initializeStatCalculators() {
    const form = document.querySelector('.add-player-form');
    if (!form) return;
    
    const killsInput = form.querySelector('input[name="kills"]');
    const deathsInput = form.querySelector('input[name="deaths"]');
    const winsInput = form.querySelector('input[name="wins"]');
    const gamesInput = form.querySelector('input[name="games_played"]');
    
    if (killsInput && deathsInput) {
        [killsInput, deathsInput].forEach(input => {
            input.addEventListener('input', () => updateKDPreview(killsInput, deathsInput));
        });
    }
    
    if (winsInput && gamesInput) {
        [winsInput, gamesInput].forEach(input => {
            input.addEventListener('input', () => updateWinRatePreview(winsInput, gamesInput));
        });
    }
}

function updateKDPreview(killsInput, deathsInput) {
    const kills = parseInt(killsInput.value) || 0;
    const deaths = parseInt(deathsInput.value) || 0;
    const kd = deaths > 0 ? (kills / deaths).toFixed(2) : kills;
    
    showStatPreview(killsInput, `K/D: ${kd}`);
}

function updateWinRatePreview(winsInput, gamesInput) {
    const wins = parseInt(winsInput.value) || 0;
    const games = parseInt(gamesInput.value) || 0;
    const winRate = games > 0 ? ((wins / games) * 100).toFixed(1) : 0;
    
    showStatPreview(winsInput, `Побед: ${winRate}%`);
}

function showStatPreview(input, text) {
    let preview = input.parentNode.querySelector('.stat-preview');
    if (!preview) {
        preview = document.createElement('small');
        preview.className = 'stat-preview text-muted mt-1';
        input.parentNode.appendChild(preview);
    }
    preview.textContent = text;
}

// Auto-save functionality
function initializeAutoSave() {
    const adminForm = document.querySelector('.add-player-form');
    if (!adminForm) return;
    
    const inputs = adminForm.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('input', debounce(saveFormData, 1000));
    });
    
    // Load saved data on page load
    loadFormData();
}

function saveFormData() {
    const form = document.querySelector('.add-player-form');
    if (!form) return;
    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    localStorage.setItem('bedwars_form_data', JSON.stringify(data));
    
    // Show save indicator
    showSaveIndicator();
}

function loadFormData() {
    const savedData = localStorage.getItem('bedwars_form_data');
    if (!savedData) return;
    
    try {
        const data = JSON.parse(savedData);
        const form = document.querySelector('.add-player-form');
        if (!form) return;
        
        Object.entries(data).forEach(([name, value]) => {
            const input = form.querySelector(`[name="${name}"]`);
            if (input && value) {
                input.value = value;
            }
        });
    } catch (error) {
        console.error('Error loading form data:', error);
    }
}

function showSaveIndicator() {
    let indicator = document.querySelector('.save-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'save-indicator position-fixed bottom-0 end-0 m-3 p-2 bg-success text-white rounded';
        indicator.style.zIndex = '9999';
        indicator.style.opacity = '0';
        indicator.style.transition = 'opacity 0.3s ease';
        indicator.innerHTML = '<i class="fas fa-check me-1"></i>Сохранено';
        document.body.appendChild(indicator);
    }
    
    indicator.style.opacity = '1';
    setTimeout(() => {
        indicator.style.opacity = '0';
    }, 2000);
}

// Search Functionality
function initializeSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    if (!searchInput) return;
    
    // Add search enhancements
    addSearchSuggestions(searchInput);
    addSearchFilters();
}

function addSearchSuggestions(searchInput) {
    const suggestions = document.createElement('div');
    suggestions.className = 'search-suggestions position-absolute bg-dark border rounded mt-1 w-100';
    suggestions.style.zIndex = '1000';
    suggestions.style.display = 'none';
    
    searchInput.parentNode.appendChild(suggestions);
    
    searchInput.addEventListener('input', debounce(() => {
        updateSearchSuggestions(searchInput, suggestions);
    }, 300));
    
    searchInput.addEventListener('blur', () => {
        setTimeout(() => {
            suggestions.style.display = 'none';
        }, 200);
    });
}

function updateSearchSuggestions(searchInput, suggestionsDiv) {
    const query = searchInput.value.trim().toLowerCase();
    if (query.length < 2) {
        suggestionsDiv.style.display = 'none';
        return;
    }
    
    // Get player names from current page
    const playerNames = Array.from(document.querySelectorAll('.player-name'))
        .map(el => el.textContent.trim())
        .filter(name => name.toLowerCase().includes(query))
        .slice(0, 5);
    
    if (playerNames.length === 0) {
        suggestionsDiv.style.display = 'none';
        return;
    }
    
    suggestionsDiv.innerHTML = playerNames
        .map(name => `<div class="search-suggestion p-2 cursor-pointer hover:bg-secondary">${name}</div>`)
        .join('');
    
    suggestionsDiv.style.display = 'block';
    
    // Add click handlers
    suggestionsDiv.querySelectorAll('.search-suggestion').forEach(suggestion => {
        suggestion.addEventListener('click', () => {
            searchInput.value = suggestion.textContent;
            suggestionsDiv.style.display = 'none';
            searchInput.form.submit();
        });
    });
}

function addSearchFilters() {
    const searchForm = document.querySelector('.search-form');
    if (!searchForm) return;
    
    // Add quick filter buttons
    const filtersDiv = document.createElement('div');
    filtersDiv.className = 'search-filters mt-2';
    filtersDiv.innerHTML = `
        <small class="text-muted">Быстрые фильтры:</small>
        <div class="btn-group btn-group-sm mt-1" role="group">
            <button type="button" class="btn btn-outline-secondary" data-filter="level:high">Высокий уровень</button>
            <button type="button" class="btn btn-outline-secondary" data-filter="kd:good">Хороший K/D</button>
            <button type="button" class="btn btn-outline-secondary" data-filter="active">Активные</button>
        </div>
    `;
    
    searchForm.appendChild(filtersDiv);
    
    // Add filter functionality
    filtersDiv.querySelectorAll('[data-filter]').forEach(btn => {
        btn.addEventListener('click', () => {
            applyQuickFilter(btn.dataset.filter);
        });
    });
}

function applyQuickFilter(filter) {
    const rows = document.querySelectorAll('.player-row');
    
    rows.forEach(row => {
        let show = true;
        
        switch (filter) {
            case 'level:high':
                const levelText = row.querySelector('.level-badge, .stat-value')?.textContent || '0';
                const level = parseInt(levelText.replace('Уровень ', '').replace('Level ', ''));
                show = level >= 25;
                break;
            case 'kd:good':
                const kdText = row.querySelector('.stat-value')?.textContent || '0';
                const kd = parseFloat(kdText);
                show = kd >= 1.5;
                break;
            case 'active':
                const games = parseInt(row.querySelector('.player-row td:nth-child(8)')?.textContent || '0');
                show = games >= 50;
                break;
        }
        
        row.style.display = show ? '' : 'none';
    });
}

// Mobile Optimizations
function initializeMobileOptimizations() {
    if (!isMobileDevice()) return;
    
    // Add mobile-specific styles
    document.body.classList.add('mobile-device');
    
    // Optimize table for mobile
    optimizeTableForMobile();
    
    // Add touch gestures
    addTouchGestures();
    
    // Optimize forms for mobile
    optimizeFormsForMobile();
}

function isMobileDevice() {
    return window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

function optimizeTableForMobile() {
    const table = document.querySelector('.leaderboard-table');
    if (!table) return;
    
    // Add horizontal scroll indicator
    const scrollIndicator = document.createElement('div');
    scrollIndicator.className = 'mobile-scroll-indicator text-center text-muted small py-2';
    scrollIndicator.innerHTML = '<i class="fas fa-arrows-alt-h me-1"></i>Прокрутите влево/вправо для просмотра';
    
    table.parentNode.insertBefore(scrollIndicator, table);
    
    // Add swipe detection
    let startX = 0;
    table.addEventListener('touchstart', e => {
        startX = e.touches[0].clientX;
    });
    
    table.addEventListener('touchmove', e => {
        const currentX = e.touches[0].clientX;
        const diff = startX - currentX;
        
        if (Math.abs(diff) > 10) {
            scrollIndicator.style.opacity = '0.5';
        }
    });
    
    table.addEventListener('touchend', () => {
        setTimeout(() => {
            scrollIndicator.style.opacity = '1';
        }, 1000);
    });
}

function addTouchGestures() {
    // Add pull-to-refresh functionality
    let startY = 0;
    let isPulling = false;
    
    document.addEventListener('touchstart', e => {
        startY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchmove', e => {
        const currentY = e.touches[0].clientY;
        const diff = currentY - startY;
        
        if (diff > 50 && window.scrollY === 0) {
            isPulling = true;
            showPullToRefreshIndicator();
        }
    });
    
    document.addEventListener('touchend', () => {
        if (isPulling) {
            isPulling = false;
            hidePullToRefreshIndicator();
            setTimeout(() => {
                window.location.reload();
            }, 500);
        }
    });
}

function showPullToRefreshIndicator() {
    let indicator = document.querySelector('.pull-to-refresh-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'pull-to-refresh-indicator position-fixed top-0 start-0 end-0 bg-warning text-dark text-center py-2';
        indicator.style.zIndex = '9999';
        indicator.innerHTML = '<i class="fas fa-sync-alt me-1"></i>Отпустите для обновления';
        document.body.appendChild(indicator);
    }
    indicator.style.display = 'block';
}

function hidePullToRefreshIndicator() {
    const indicator = document.querySelector('.pull-to-refresh-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

function optimizeFormsForMobile() {
    // Add mobile-friendly input types
    document.querySelectorAll('input[name*="experience"], input[name*="kills"], input[name*="deaths"]').forEach(input => {
        input.setAttribute('inputmode', 'numeric');
        input.setAttribute('pattern', '[0-9]*');
    });
    
    // Auto-hide keyboard on enter
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('keydown', e => {
            if (e.key === 'Enter') {
                input.blur();
            }
        });
    });
}

// Keyboard Shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

function handleKeyboardShortcuts(e) {
    // Admin shortcuts (Ctrl/Cmd + key)
    if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
            case 'k':
                e.preventDefault();
                focusSearch();
                break;
            case 'n':
                if (isAdmin()) {
                    e.preventDefault();
                    goToAddPlayer();
                }
                break;
            case 's':
                if (isAdmin()) {
                    e.preventDefault();
                    goToStatistics();
                }
                break;
        }
    }
    
    // Navigation shortcuts
    switch (e.key) {
        case 'Escape':
            closeModals();
            break;
        case 'h':
            if (!isInputFocused()) {
                goToHome();
            }
            break;
    }
}

function focusSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        searchInput.focus();
        searchInput.select();
    }
}

function isAdmin() {
    return document.querySelector('.nav-link[href*="admin"]') !== null;
}

function isInputFocused() {
    const activeElement = document.activeElement;
    return activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA' || activeElement.tagName === 'SELECT');
}

function goToAddPlayer() {
    const adminLink = document.querySelector('.nav-link[href*="admin"]');
    if (adminLink) {
        window.location.href = adminLink.href;
    }
}

function goToStatistics() {
    const statsLink = document.querySelector('.nav-link[href*="statistics"]');
    if (statsLink) {
        window.location.href = statsLink.href;
    }
}

function goToHome() {
    window.location.href = '/';
}

function closeModals() {
    const modals = document.querySelectorAll('.modal.show');
    modals.forEach(modal => {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
    });
}

// Performance Monitoring
function initializePerformanceMonitoring() {
    // Monitor page load performance
    window.addEventListener('load', () => {
        setTimeout(logPerformanceMetrics, 1000);
    });
    
    // Monitor user interactions
    monitorUserInteractions();
    
    // Monitor errors
    monitorErrors();
}

function logPerformanceMetrics() {
    if ('performance' in window) {
        const navigation = performance.getEntriesByType('navigation')[0];
        const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
        
        console.log('🚀 Performance Metrics:', {
            'Load Time': `${loadTime.toFixed(2)}ms`,
            'DOM Content Loaded': `${navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart}ms`,
            'Total Page Load': `${navigation.loadEventEnd - navigation.navigationStart}ms`
        });
    }
}

function monitorUserInteractions() {
    // Track click events
    document.addEventListener('click', e => {
        if (e.target.classList.contains('btn') || e.target.closest('.btn')) {
            const button = e.target.classList.contains('btn') ? e.target : e.target.closest('.btn');
            logInteraction('button_click', {
                text: button.textContent.trim(),
                classes: button.className
            });
        }
    });
    
    // Track form submissions
    document.addEventListener('submit', e => {
        logInteraction('form_submit', {
            form: e.target.className,
            action: e.target.action
        });
    });
}

function monitorErrors() {
    window.addEventListener('error', e => {
        console.error('🚨 JavaScript Error:', {
            message: e.message,
            filename: e.filename,
            line: e.lineno,
            column: e.colno
        });
    });
    
    window.addEventListener('unhandledrejection', e => {
        console.error('🚨 Unhandled Promise Rejection:', e.reason);
    });
}

function logInteraction(type, data) {
    if (window.console && console.log) {
        console.log(`📊 User Interaction: ${type}`, data);
    }
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function formatNumber(num) {
    return new Intl.NumberFormat('ru-RU').format(num);
}

function calculateKD(kills, deaths) {
    return deaths > 0 ? (kills / deaths).toFixed(2) : kills;
}

function calculateWinRate(wins, games) {
    return games > 0 ? ((wins / games) * 100).toFixed(1) : 0;
}

// Easter Eggs & Fun Features
function initializeEasterEggs() {
    // Konami code
    let konamiCode = [];
    const konamiSequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // ↑↑↓↓←→←→BA
    
    document.addEventListener('keydown', e => {
        konamiCode.push(e.keyCode);
        if (konamiCode.length > konamiSequence.length) {
            konamiCode.shift();
        }
        
        if (konamiCode.join(',') === konamiSequence.join(',')) {
            activatePartyMode();
            konamiCode = [];
        }
    });
    
    // Secret admin features
    if (isAdmin() && new Date().getHours() === 0) {
        addMidnightEffects();
    }
}

function activatePartyMode() {
    document.body.style.animation = 'rainbow 2s infinite';
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes rainbow {
            0% { filter: hue-rotate(0deg); }
            100% { filter: hue-rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    
    // Create confetti effect
    createConfetti();
    
    setTimeout(() => {
        document.body.style.animation = '';
        style.remove();
    }, 10000);
    
    console.log('🎉 PARTY MODE ACTIVATED! 🎉');
}

function createConfetti() {
    for (let i = 0; i < 50; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: fixed;
                top: -10px;
                left: ${Math.random() * 100}vw;
                width: 10px;
                height: 10px;
                background: hsl(${Math.random() * 360}, 100%, 50%);
                pointer-events: none;
                z-index: 9999;
                animation: fall 3s linear infinite;
            `;
            
            document.body.appendChild(confetti);
            
            setTimeout(() => confetti.remove(), 3000);
        }, i * 100);
    }
    
    if (!document.querySelector('#fall-animation')) {
        const style = document.createElement('style');
        style.id = 'fall-animation';
        style.textContent = `
            @keyframes fall {
                to {
                    transform: translateY(100vh) rotate(360deg);
                }
            }
        `;
        document.head.appendChild(style);
    }
}

function addMidnightEffects() {
    document.body.classList.add('midnight-mode');
    
    const style = document.createElement('style');
    style.textContent = `
        .midnight-mode {
            filter: hue-rotate(45deg) brightness(0.8);
        }
    `;
    document.head.appendChild(style);
}

// Initialize easter eggs
setTimeout(initializeEasterEggs, 2000);

// Export functions for global access
window.BedwarsLeaderboard = {
    formatNumber,
    calculateKD,
    calculateWinRate,
    debounce,
    throttle,
    logInteraction
};
