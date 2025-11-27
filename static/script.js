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
    initCartFunctionality(); // This will handle cart initialization
    initHamburgerMenu();
    initCategorySwitcher();
    initProfileDropdown();
    initPasswordToggle();
    
    isInitialized = true;
    console.log('✅ All modules initialized');
}

// Single initialization point
document.addEventListener('DOMContentLoaded', initializeAll);

// =========================
// 1. HEADER SCROLL EFFECT
// =========================
function initHeaderEffects() {
    const header = document.querySelector('.hero-header');
    if (!header) return;
    
    window.addEventListener('scroll', function() {
        header.classList.toggle('scrolled', window.scrollY > 0);
    });
}

// =========================
// 2. IMAGE SLIDER
// =========================
function initImageSlider() {
    const slider = document.getElementById('imageSlider');
    if (!slider) return;
    
    function autoScroll() {
        const maxScrollLeft = slider.scrollWidth - slider.clientWidth;
        
        if (Math.ceil(slider.scrollLeft) >= maxScrollLeft) {
            slider.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
            slider.scrollBy({ left: 320, behavior: 'smooth' });
        }
    }
    
    setInterval(autoScroll, 3000);
}

// =========================
// 3. SEARCH FUNCTIONALITY
// =========================
function initSearchFunctionality() {
    const searchToggle = document.getElementById('searchToggle');
    const searchContainer = document.querySelector('.search-container');
    const searchBox = document.getElementById('searchBox');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    
    if (!searchToggle || !searchContainer || !searchBox || !searchInput || !searchResults) {
        console.log('❌ Search elements missing');
        return;
    }
    
    // Remove debug styles
    searchResults.removeAttribute('style');
    
    // Search toggle
    searchToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        searchContainer.classList.contains('active') ? closeSearch() : openSearch();
    });
    
    // Real-time search
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.trim();
        if (searchTerm.length > 2) {
            performSearch(searchTerm, searchResults);
            searchBox.classList.add('has-results');
        } else {
            hideResults(searchResults);
            searchBox.classList.remove('has-results');
        }
    });
    
    // Close search when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-container')) {
            closeSearch();
        }
    });
    
    // Close on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeSearch();
    });
    
    function openSearch() {
        searchContainer.classList.add('active');
        setTimeout(() => searchInput.focus(), 300);
    }
    
    function closeSearch() {
        searchContainer.classList.remove('active');
        searchInput.value = '';
        hideResults(searchResults);
        searchBox.classList.remove('has-results');
    }
    
    function hideResults(resultsElement) {
        resultsElement?.classList.remove('active');
    }
}

function performSearch(searchTerm, searchResultsElement) {
    fetch(`/api/search/?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.ok ? response.json() : Promise.reject('API error'))
        .then(data => displaySearchResults(data.results, searchResultsElement))
        .catch(error => {
            console.error('Search error:', error);
            searchResultsElement.innerHTML = `<p class="search-error">No results found.</p>`;
        });
}

fetch(`/api/search/?q=${encodeURIComponent(searchTerm)}`)

function displaySearchResults(results, searchResultsElement) {
    if (!searchResultsElement) return;
    
    if (results?.length > 0) {
        searchResultsElement.innerHTML = results.map(product => `
            <div class="search-result-item" data-product-id="${product.id}">
                <div class="product-name">${product.name}</div>
                <div class="product-price">${product.price}</div>
            </div>
        `).join('');
        
        // Add click events to results
        searchResultsElement.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', function() {
                const productId = this.dataset.productId;
                const product = results.find(p => p.id == productId);
                window.location.href = product?.url || `/product/${productId}/`;
            });
        });
    } else {
        searchResultsElement.innerHTML = '<div class="no-results">No products found</div>';
    }
    
    searchResultsElement.classList.add('active');
}

// =========================
// 4. CART FUNCTIONALITY (FOR POPUP ONLY) - FIXED VERSION
// =========================
let searchTerm = '';
function initCartFunctionality() {
    // Only initialize if cart popup exists (shop now page)
    const cartPopup = document.getElementById("cart-popup");
    if (!cartPopup) {
        console.log('🛒 Cart popup not found - skipping initialization');
        return;
    }
    
    console.log('🛒 Initializing cart functionality...');
    loadCartData();
    initCartToggle();
    initCartButtons();
}

// Load real cart data from server - FIXED ENDPOINT
async function loadCartData() {
    try {
        const response = await fetch('/api/cart/data/'); // FIXED: Correct endpoint
        if (response.ok) {
            const cartData = await response.json();
            console.log('🛒 Server cart data:', cartData);
            updateCartDisplay(cartData);
        } else {
            console.log('❌ Failed to load cart data');
            updateCartTotals(); // Fallback to client-side calculation
        }
    } catch (error) {
        console.error('🛒 Error loading cart data:', error);
        updateCartTotals(); // Fallback to client-side calculation
    }
}

// Update cart display with real server data AND DOM state - IMPROVED
function updateCartDisplay(cartData) {
    const cartCount = document.querySelector('.cart-count');
    const totalPriceElement = document.querySelector('.total-price');
    const emptyCart = document.querySelector('.empty-cart');
    const cartContent = document.querySelector('.cart-items');
    const cartCountHeader = document.querySelector('.cart-count-header');
    const itemsCountElement = document.querySelector('.items-count');
    const itemsSubtotalElement = document.querySelector('.items-subtotal');
    const cartSummary = document.querySelector('.cart-summary');
    const cartButtons = document.querySelector('.cart-buttons');

    console.log('📊 Updating cart display - Server data:', cartData);

    // Use server data when available, otherwise use DOM state
    let totalItems, totalPrice;

    if (cartData && cartData.success !== false) {
        // Use server data
        totalItems = cartData.total_items || 0;
        totalPrice = cartData.total_price || 0;
        console.log('🔄 Using SERVER data for totals');
    } else {
        // Fallback to DOM calculation
        totalItems = calculateDomItemCount();
        totalPrice = calculateDomTotal();
        console.log('🔄 Using DOM data for totals');
    }

    // Update header counts
    if (cartCountHeader) cartCountHeader.textContent = totalItems;
    if (cartCount) cartCount.textContent = totalItems;

    // Update summary row
    if (itemsCountElement) {
        itemsCountElement.textContent = `${totalItems} item${totalItems !== 1 ? 's' : ''}`;
    }

    if (itemsSubtotalElement) {
        itemsSubtotalElement.textContent = `¥${totalPrice.toFixed(2)}`;
    }

    // Update total price
    if (totalPriceElement) {
        totalPriceElement.textContent = `¥${totalPrice.toFixed(2)}`;
        console.log('🔄 Total price updated to:', totalPrice);
    }

    // Handle empty cart state
    const isEmpty = totalItems === 0;
    
    if (emptyCart) emptyCart.style.display = isEmpty ? 'block' : 'none';
    if (cartContent) cartContent.style.display = isEmpty ? 'none' : 'block';
    if (cartSummary) cartSummary.style.display = isEmpty ? 'none' : 'block';
    if (cartButtons) cartButtons.style.display = isEmpty ? 'none' : 'block';

    console.log('🛒 Cart empty state:', isEmpty);
}

// Calculate total items from DOM (sum of quantities) - NEW FUNCTION
function calculateDomItemCount() {
    const items = document.querySelectorAll('.cart-item');
    let totalItems = 0;
    
    items.forEach(item => {
        const quantity = parseInt(item.querySelector('.quantity').textContent) || 0;
        totalItems += quantity;
    });
    
    console.log('🧮 DOM calculated item count:', totalItems);
    return totalItems;
}

// Calculate total price from DOM items as fallback
function calculateDomTotal() {
    const items = document.querySelectorAll('.cart-item');
    let total = 0;
    
    items.forEach(item => {
        const quantity = parseInt(item.querySelector('.quantity').textContent) || 0;
        const priceElement = item.querySelector('.item-price');
        
        if (priceElement) {
            const priceText = priceElement.textContent.replace('¥', '').replace('$', '').trim();
            const price = parseFloat(priceText) || 0;
            total += quantity * price;
        }
    });
    
    console.log('🧮 DOM calculated total:', total);
    return total;
}

/* ============================
   UPDATE QUANTITY (AJAX) - IMPROVED
============================ */
async function updateQuantity(button, change) {
    const item = button.closest(".cart-item");
    const quantityEl = item.querySelector(".quantity");
    const itemId = button.dataset.itemId;

    let currentQty = parseInt(quantityEl.textContent);
    let newQty = currentQty + change;
    
    console.log('🔄 Updating quantity:', { itemId, currentQty, newQty, change });
    
    // Don't allow quantity less than 1
    if (newQty < 1) {
        if (confirm("Remove this item from cart?")) {
            await removeItem(button);
        }
        return;
    }

    // Update UI immediately for better UX
    quantityEl.textContent = newQty;
    item.classList.add('updating');
    
    try {
        // Send update to backend
        const response = await fetch("/api/cart/update/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ item_id: itemId, quantity: newQty })
        });

        if (response.ok) {
            const result = await response.json();
            console.log('✅ Quantity updated:', result);
            
            if (result.success) {
                // Update totals with server data
                updateCartDisplay(result);
            } else {
                throw new Error(result.error);
            }
        } else {
            throw new Error('Failed to update quantity');
        }
    } catch (error) {
        console.error('🛒 Error updating quantity:', error);
        // Revert UI if server update failed
        quantityEl.textContent = currentQty;
        updateCartTotals(); // Fallback to client calculation
    } finally {
        item.classList.remove('updating');
    }
}

/* ============================
   REMOVE ITEM (AJAX) - IMPROVED
============================ */
async function removeItem(button) {
    const item = button.closest(".cart-item");
    const itemId = button.dataset.itemId;

    console.log('🗑️ Removing item:', itemId);

    // Visual feedback
    item.style.opacity = "0.5";
    item.style.pointerEvents = "none";
    
    try {
        // Send remove request to backend
        const response = await fetch("/api/cart/remove/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ item_id: itemId })
        });

        if (response.ok) {
            const result = await response.json();
            console.log('✅ Item removed:', result);
            
            if (result.success) {
                // Remove from UI after successful server removal
                setTimeout(() => {
                    item.remove();
                    // Update totals with server data
                    updateCartDisplay(result);
                }, 300);
            } else {
                throw new Error(result.error);
            }
        } else {
            throw new Error('Failed to remove item');
        }
    } catch (error) {
        console.error('🛒 Error removing item:', error);
        // Revert visual feedback on error
        item.style.opacity = "1";
        item.style.pointerEvents = "auto";
        updateCartTotals(); // Fallback to client calculation
    }
}

/* ============================
   UPDATE CART TOTALS (CLIENT-SIDE FALLBACK) - IMPROVED
============================ */
function updateCartTotals() {
    const items = document.querySelectorAll(".cart-item");
    const cartCount = document.querySelector(".cart-count");
    const cartCountHeader = document.querySelector(".cart-count-header");
    const emptyCart = document.querySelector(".empty-cart");
    const cartItems = document.querySelector(".cart-items");
    const cartSummary = document.querySelector(".cart-summary");
    const cartButtons = document.querySelector(".cart-buttons");
    const totalPriceElement = document.querySelector(".total-price");
    const itemsCountElement = document.querySelector(".items-count");
    const itemsSubtotalElement = document.querySelector(".items-subtotal");

    let total = 0;
    let totalItems = 0;

    items.forEach(item => {
        const qty = parseInt(item.querySelector(".quantity").textContent);
        const priceElement = item.querySelector('.item-price');
        
        if (priceElement) {
            const priceText = priceElement.textContent.replace('¥', '').replace('$', '').trim();
            const unitPrice = parseFloat(priceText) || 0;
            total += qty * unitPrice;
            totalItems += qty;
        }
    });

    // Update header counts
    if (cartCount) cartCount.textContent = totalItems;
    if (cartCountHeader) cartCountHeader.textContent = totalItems;

    // Update summary elements
    if (itemsCountElement) {
        itemsCountElement.textContent = `${totalItems} item${totalItems !== 1 ? 's' : ''}`;
    }

    if (itemsSubtotalElement) {
        itemsSubtotalElement.textContent = `¥${total.toFixed(2)}`;
    }

    // Update total price
    if (totalPriceElement) {
        totalPriceElement.textContent = `¥${total.toFixed(2)}`;
    }

    // Empty cart display
    const isEmpty = items.length === 0;
    if (emptyCart) emptyCart.style.display = isEmpty ? "block" : "none";
    if (cartItems) cartItems.style.display = isEmpty ? "none" : "block";
    if (cartSummary) cartSummary.style.display = isEmpty ? "none" : "block";
    if (cartButtons) cartButtons.style.display = isEmpty ? "none" : "block";
    
    console.log('🛒 Client-side totals updated:', { totalItems, total });
}

// =========================
// UTILITY FUNCTIONS
// =========================
function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

// Remove the duplicate initCartFunctionality function and calculateDomSubtotal if not needed

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initCartFunctionality();
});

/* ============================
   CART TOGGLE - MISSING FUNCTION
============================ */
function initCartToggle() {
    const cartToggle = document.getElementById("cart-toggle");
    const cartPopup = document.getElementById("cart-popup");
    const closeCart = document.querySelector(".close-cart");

    console.log('🛒 Cart toggle elements:', { cartToggle, cartPopup, closeCart });

    if (!cartToggle || !cartPopup) {
        console.log('❌ Cart toggle elements missing');
        return;
    }

    cartToggle.addEventListener("click", async (e) => {
        e.preventDefault();
        console.log('🎯 Cart toggle clicked');
        cartPopup.classList.toggle("active");
        
        // Reload cart data when opening cart
        if (cartPopup.classList.contains("active")) {
            await loadCartData();
        }
    });

    if (closeCart) {
        closeCart.addEventListener("click", () => {
            cartPopup.classList.remove("active");
        });
    }

    // Click outside to close
    document.addEventListener("click", (e) => {
        if (
            cartPopup.classList.contains("active") &&
            !cartPopup.contains(e.target) &&
            !cartToggle.contains(e.target)
        ) {
            cartPopup.classList.remove("active");
        }
    });
}

/* ============================
   CART BUTTONS (+, -, Remove) - MISSING FUNCTION
============================ */
function initCartButtons() {
    // PLUS - Update quantity
    document.querySelectorAll(".quantity-btn.plus").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            await updateQuantity(btn, +1);
        });
    });

    // MINUS - Update quantity
    document.querySelectorAll(".quantity-btn.minus").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            await updateQuantity(btn, -1);
        });
    });

    // DELETE - Remove item
    document.querySelectorAll(".remove-btn").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            if (confirm("Remove this item from cart?")) {
                await removeItem(btn);
            }
        });
    });
}

// Debug function
function debugCart() {
    console.log('=== CART DEBUG ===');
    const items = document.querySelectorAll('.cart-item');
    console.log('Cart items found:', items.length);
    
    items.forEach((item, index) => {
        const itemId = item.dataset.itemId;
        const quantity = item.querySelector('.quantity').textContent;
        const price = item.querySelector('.item-price').textContent;
        console.log(`Item ${index}: ID=${itemId}, Qty=${quantity}, Price=${price}`);
    });
    
    // Test server connection
    fetch('/api/cart/')
        .then(response => response.json())
        .then(data => console.log('Server cart data:', data))
        .catch(error => console.log('Server connection error:', error));
}

// =========================
// 5. HAMBURGER MENU (FIXED VERSION)
// =========================
function initHamburgerMenu() {
    console.log('🍔 Initializing hamburger menu...');
    
    const hamburgerToggle = document.getElementById('hamburgerToggle');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const dropdownClose = document.getElementById('dropdownClose');

    console.log('🍔 Hamburger elements:', {
        toggle: hamburgerToggle,
        menu: dropdownMenu,
        close: dropdownClose
    });

    if (!hamburgerToggle || !dropdownMenu) {
        console.log('❌ Hamburger elements not found');
        return;
    }

    // Set initial state
    dropdownMenu.style.display = 'none';

    // Hamburger toggle click
    hamburgerToggle.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('🎯 Hamburger clicked - current display:', dropdownMenu.style.display);
        
        if (dropdownMenu.style.display === 'block') {
            dropdownMenu.style.display = 'none';
            console.log('🍔 Menu hidden');
        } else {
            dropdownMenu.style.display = 'block';
            console.log('🍔 Menu shown');
        }
    });

    // Close button click
    if (dropdownClose) {
        dropdownClose.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('🎯 Close button clicked');
            dropdownMenu.style.display = 'none';
        });
    }

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (dropdownMenu.style.display === 'block') {
            if (!dropdownMenu.contains(e.target) && !hamburgerToggle.contains(e.target)) {
                console.log('🍔 Menu closed (outside click)');
                dropdownMenu.style.display = 'none';
            }
        }
    });

    // Close menu on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && dropdownMenu.style.display === 'block') {
            console.log('🍔 Menu closed (Escape key)');
            dropdownMenu.style.display = 'none';
        }
    });

    console.log('✅ Hamburger menu initialized successfully');
}

// =========================
// 6. CATEGORY SWITCHER
// =========================
function initCategorySwitcher() {
    const categoryBtns = document.querySelectorAll('.category-btn');
    const categoryContents = document.querySelectorAll('.category-content');
    
    if (categoryBtns.length === 0) return;
    
    // Show first category by default
    if (categoryContents.length > 0) {
        categoryContents[0].classList.add('active');
        categoryBtns[0].classList.add('active');
    }
    
    categoryBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all
            categoryBtns.forEach(b => b.classList.remove('active'));
            categoryContents.forEach(c => c.classList.remove('active'));
            
            // Add active to clicked
            this.classList.add('active');
            const categoryId = this.dataset.category;
            const targetContent = document.getElementById(`category-${categoryId}`);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

// =========================
// 7. PROFILE DROPDOWN
// =========================
function initProfileDropdown() {
    const profileToggle = document.querySelector('.profile-toggle');
    const dropdownContent = document.querySelector('.dropdown-content');
    
    if (!profileToggle || !dropdownContent) return;
    
    profileToggle.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropdownContent.classList.toggle('active');
    });
    
    // Close when clicking outside
    document.addEventListener('click', function() {
        dropdownContent.classList.remove('active');
    });
    
    // Keep open when clicking inside
    dropdownContent.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    
    // Close on escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') dropdownContent.classList.remove('active');
    });
}

// =========================
// 8. PASSWORD TOGGLE
// =========================
function initPasswordToggle() {
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('id_password');
    
    if (!togglePassword || !passwordInput) return;
    
    const eyeIcon = togglePassword.querySelector('i');
    
    togglePassword.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        if (eyeIcon) {
            if (type === 'text') {
                eyeIcon.classList.replace('fa-eye', 'fa-eye-slash');
                togglePassword.setAttribute('aria-label', 'Hide password');
            } else {
                eyeIcon.classList.replace('fa-eye-slash', 'fa-eye');
                togglePassword.setAttribute('aria-label', 'Show password');
            }
        }
    });
    
    // Keyboard accessibility
    togglePassword.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            this.click();
        }
    });
}

// =========================
// UTILITY FUNCTIONS (FIXED CSRF)
// =========================
function getCSRFToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    // Method 2: Get from cookie
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    
    if (cookieValue) {
        return cookieValue;
    }
    
    // Method 3: Get from meta tag
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        return metaToken.getAttribute('content');
    }
    
    console.error('❌ CSRF token not found!');
    return '';
}

fetch('/api/cart/data/')

