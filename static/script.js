document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - starting initialization');

    // Initialize all functionality
    initHeaderEffects();
    initImageSlider();
    initSearchFunctionality();
    initCartFunctionality();
    initHamburgerMenu();
    initCategorySwitcher();
    initProfileDropdown();

    console.log('Initialization complete');
});

// =========================
// HEADER SCROLL EFFECT
// =========================
function initHeaderEffects() {
    const header = document.querySelector('.hero-header');
    if (header) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 0) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }
}

// =========================
// IMAGE SLIDER
// =========================
function initImageSlider() {
    const slider = document.getElementById('imageSlider');

    function autoScroll() {
        if (!slider) return;
        const maxScrollLeft = slider.scrollWidth - slider.clientWidth;

        if (Math.ceil(slider.scrollLeft) >= maxScrollLeft) {
            slider.scrollTo({ 
                left: 0, 
                behavior: 'smooth' 
            });
        } else {
            slider.scrollBy({ 
                left: 320, 
                behavior: 'smooth' 
            });
        }
    }

    if (slider) {
        setInterval(autoScroll, 3000);
    }
}

// =========================
// SEARCH FUNCTIONALITY - FIXED VERSION
// =========================
function initSearchFunctionality() {
    const searchToggle = document.getElementById('searchToggle');
    const searchContainer = document.querySelector('.search-container');
    const searchBox = document.getElementById('searchBox');
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.querySelector('.search-form');
    const searchResults = document.getElementById('searchResults');

    console.log('🔍 Search elements:', {
        searchToggle: !!searchToggle,
        searchContainer: !!searchContainer,
        searchBox: !!searchBox,
        searchInput: !!searchInput,
        searchResults: !!searchResults
    });

    if (searchToggle && searchContainer && searchBox && searchInput && searchResults) {
        console.log('✅ All search elements found - initializing');
        
        // REMOVE DEBUG STYLES - THIS IS CRITICAL!
        searchResults.removeAttribute('style');
        
        // Toggle search when clicking the header button
        searchToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            console.log('🎯 Search toggle clicked');
            
            if (searchContainer.classList.contains('active')) {
                closeSearch();
            } else {
                openSearch();
            }
        });

        // Handle search input (real-time search)
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.trim();
            console.log('⌨️ Input event:', searchTerm);
            
            if (searchTerm.length > 2) {
                console.log('🔍 Performing search for:', searchTerm);
                performSearch(searchTerm, searchResults);
                searchBox.classList.add('has-results');
            } else {
                hideResults(searchResults);
                searchBox.classList.remove('has-results');
            }
        });

        // Handle search form submission
        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const searchTerm = searchInput.value.trim();
                console.log('📤 Form submitted:', searchTerm);
                if (searchTerm) {
                    performSearch(searchTerm, searchResults);
                    searchBox.classList.add('has-results');
                }
            });
        }

        // Close search when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.search-container')) {
                closeSearch();
            }
        });

        // Close on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeSearch();
            }
        });

        function openSearch() {
            searchContainer.classList.add('active');
            console.log('✅ Search opened');
            setTimeout(() => {
                searchInput.focus();
                console.log('🎯 Input focused');
            }, 300);
        }

        function closeSearch() {
            searchContainer.classList.remove('active');
            searchInput.value = '';
            hideResults(searchResults);
            searchBox.classList.remove('has-results');
            console.log('❌ Search closed');
        }

        function hideResults(resultsElement) {
            if (resultsElement) {
                resultsElement.classList.remove('active');
                console.log('📭 Results hidden');
            }
        }
    } else {
        console.log('❌ Missing search elements');
    }
}

function performSearch(searchTerm, searchResultsElement) {
    console.log('🚀 API Search for:', searchTerm);
    
    // Real API call to your Django backend
    fetch(`/api/search/?q=${encodeURIComponent(searchTerm)}`)
        .then(response => {
            console.log('📡 API Response status:', response.status);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('📦 API Data received:', data);
            displaySearchResults(data.results, searchResultsElement);
        })
        .catch(error => {
            console.error('❌ Search error:', error);
            // Fallback to mock data if API fails
            const mockResults = [
                { id: 1, name: 'Product A', price: '$19.99', url: '/product/1/' },
                { id: 2, name: 'Product B', price: '$29.99', url: '/product/2/' }
            ];
            console.log('🔄 Using mock data');
            displaySearchResults(mockResults, searchResultsElement);
        });
}

function displaySearchResults(results, searchResultsElement) {
    if (!searchResultsElement) {
        console.log('❌ searchResultsElement not provided');
        return;
    }
    
    console.log('📋 Displaying results:', results);
    
    if (results && results.length > 0) {
        searchResultsElement.innerHTML = results.map(product => `
            <div class="search-result-item" data-product-id="${product.id}">
                <div class="product-name">${product.name}</div>
                <div class="product-price">${product.price}</div>
            </div>
        `).join('');
        
        console.log('✅ Results HTML updated');
        
        // Add click event to result items
        searchResultsElement.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', function() {
                const productId = this.dataset.productId;
                console.log('🖱️ Product clicked:', productId);
                const product = results.find(p => p.id == productId);
                if (product && product.url) {
                    window.location.href = product.url;
                } else {
                    window.location.href = `/product/${productId}/`;
                }
            });
        });
    } else {
        searchResultsElement.innerHTML = '<div class="no-results">No products found</div>';
        console.log('📭 No results found');
    }
    
    searchResultsElement.classList.add('active');
    console.log('👁️ Results displayed');
}

// =========================
// CART FUNCTIONALITY
// =========================
function initCartFunctionality() {
    const cartToggle = document.getElementById('cart-toggle');
    const cartPopup = document.getElementById('cart-popup');
    const closeCart = document.querySelector('.close-cart');
    
    if (cartToggle && cartPopup) {
        // Open cart when clicking cart icon
        cartToggle.addEventListener('click', function(e) {
            e.preventDefault();
            cartPopup.classList.toggle('active');
        });
        
        // Close cart when clicking X
        if (closeCart) {
            closeCart.addEventListener('click', function() {
                cartPopup.classList.remove('active');
            });
        }
        
        // Close cart when clicking outside
        document.addEventListener('click', function(e) {
            if (cartPopup.classList.contains('active')) {
                if (!cartPopup.contains(e.target) && !cartToggle.contains(e.target)) {
                    cartPopup.classList.remove('active');
                }
            }
        });
    }
    
    // Add to cart buttons functionality
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.dataset.productId;
            console.log(`🛒 Product ${productId} added to cart!`);
        });
    });
}

// =========================
// HAMBURGER MENU
// =========================
function initHamburgerMenu() {
    const hamburgerToggle = document.getElementById('hamburgerToggle');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const dropdownClose = document.getElementById('dropdownClose');

    if (hamburgerToggle && dropdownMenu) {
        hamburgerToggle.addEventListener('click', function(e) {
            e.preventDefault();
            dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
        });
    }

    if (dropdownClose) {
        dropdownClose.addEventListener('click', function(e) {
            e.preventDefault();
            dropdownMenu.style.display = 'none';
        });
    }
}

// =========================
// CATEGORY SWITCHER
// =========================
function initCategorySwitcher() {
    const categoryBtns = document.querySelectorAll('.category-btn');
    const categoryContents = document.querySelectorAll('.category-content');
    
    if (categoryBtns.length > 0) {
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
}

// =========================
// PROFILE DROPDOWN
// =========================
function initProfileDropdown() {
    const profileToggle = document.querySelector('.profile-toggle');
    const dropdownContent = document.querySelector('.dropdown-content');
    
    if (profileToggle && dropdownContent) {
        profileToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropdownContent.classList.toggle('active');
        });
        
        // Close dropdown when clicking anywhere else
        document.addEventListener('click', function() {
            dropdownContent.classList.remove('active');
        });
        
        // Keep dropdown open when clicking inside it
        dropdownContent.addEventListener('click', function(e) {
            e.stopPropagation();
        });
        
        // Close on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                dropdownContent.classList.remove('active');
            }
        });
    }
}

// Login page functionality
document.addEventListener('DOMContentLoaded', function() {
    initPasswordToggle();
});

function initPasswordToggle() {
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('id_password');
    
    if (togglePassword && passwordInput) {
        const eyeIcon = togglePassword.querySelector('i');
        
        togglePassword.addEventListener('click', function() {
            // Toggle password visibility
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Toggle eye icon
            if (eyeIcon) {
                if (type === 'text') {
                    eyeIcon.classList.remove('fa-eye');
                    eyeIcon.classList.add('fa-eye-slash');
                    togglePassword.setAttribute('aria-label', 'Hide password');
                    togglePassword.title = 'Hide password';
                } else {
                    eyeIcon.classList.remove('fa-eye-slash');
                    eyeIcon.classList.add('fa-eye');
                    togglePassword.setAttribute('aria-label', 'Show password');
                    togglePassword.title = 'Show password';
                }
            }
        });
        
        // Add keyboard accessibility
        togglePassword.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                togglePassword.click();
            }
        });
    }
}

