// =========================
// INITIALIZATION CONTROLLER
// =========================
let isInitialized = false;

function initializeAll() {
    if (isInitialized) {
        console.log('⚠️ Already initialized, skipping...');
        return;
    }
    
    console.log('🚀 Starting full initialization');
    
    // Initialize all modules
    initHeaderEffects();
    initImageSlider();
    initSearchFunctionality();
    initCartFunctionality();
    initHamburgerMenu();
    initCategorySwitcher();
    initProfileDropdown();
    initPasswordToggle();
    
    isInitialized = true;
    console.log('✅ All modules initialized');
}

// =========================
// HAMBURGER MENU
// =========================
function initHamburgerMenu() {
    console.log('🍔 Starting hamburger menu...');
    
    const hamburger = document.getElementById('hamburgerToggle');
    const menu = document.getElementById('dropdownMenu');
    const closeBtn = document.getElementById('dropdownClose');
    
    if (hamburger && menu) {
        console.log('✅ Hamburger elements found');
        
        // Hamburger click
        hamburger.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🎯 Hamburger clicked');
            
            if (menu.style.display === 'block') {
                menu.style.display = 'none';
            } else {
                menu.style.display = 'block';
            }
        });
        
        // Close button
        if (closeBtn) {
            closeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                menu.style.display = 'none';
            });
        }
        
        // Close when clicking outside
        document.addEventListener('click', function(e) {
            if (menu.style.display === 'block' && 
                !menu.contains(e.target) && 
                !hamburger.contains(e.target)) {
                menu.style.display = 'none';
            }
        });
    } else {
        console.log('❌ Hamburger elements not found');
    }
}

// Add your other JavaScript functions here...

// Start everything
document.addEventListener('DOMContentLoaded', initializeAll);