// OwlHacks Delivery Frontend Application

class OwlHacksDeliveryApp {
    constructor() {
        this.baseURL = 'http://localhost:8000/api';
        this.token = localStorage.getItem('token');
        this.currentUser = null;
        this.currentLocation = null;
        this.selectedEstablishment = null;
        this.orderItems = [];
        this.refreshInterval = null;
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        
        if (this.token) {
            await this.loadCurrentUser();
        } else {
            this.showAuthScreen();
        }
    }

    setupEventListeners() {
        // Auth form listeners
        document.getElementById('loginFormElement').addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('registerFormElement').addEventListener('submit', (e) => this.handleRegister(e));
        document.getElementById('showRegister').addEventListener('click', (e) => this.showRegisterForm(e));
        document.getElementById('showLogin').addEventListener('click', (e) => this.showLoginForm(e));
        document.getElementById('logoutBtn').addEventListener('click', () => this.logout());

        // Tab listeners
        document.getElementById('requestTab').addEventListener('click', () => this.showTab('request'));
        document.getElementById('deliverTab').addEventListener('click', () => this.showTab('deliver'));

        // Location listener
        document.getElementById('getUserLocation').addEventListener('click', () => this.getUserLocation());

        // Search listener
        document.getElementById('establishmentSearch').addEventListener('input', (e) => this.searchEstablishments(e.target.value));

        // Order form listeners
        document.getElementById('addItemBtn').addEventListener('click', () => this.addOrderItem());
        document.getElementById('requestDeliveryBtn').addEventListener('click', () => this.requestDelivery());
    }

    // Authentication Methods
    async handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        try {
            this.showLoading(true);
            const response = await fetch(`${this.baseURL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                this.token = data.access_token;
                localStorage.setItem('token', this.token);
                await this.loadCurrentUser();
                this.showAlert('Login successful!', 'success');
            } else {
                this.showAlert(data.detail || 'Login failed', 'error');
            }
        } catch (error) {
            this.showAlert('Login failed. Please try again.', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;

        if (!email.endsWith('@temple.edu')) {
            this.showAlert('Please use a valid temple.edu email address', 'error');
            return;
        }

        try {
            this.showLoading(true);
            const response = await fetch(`${this.baseURL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                this.showAlert('Registration successful! Please log in.', 'success');
                this.showLoginForm();
            } else {
                this.showAlert(data.detail || 'Registration failed', 'error');
            }
        } catch (error) {
            this.showAlert('Registration failed. Please try again.', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async loadCurrentUser() {
        try {
            const response = await fetch(`${this.baseURL}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            });

            if (response.ok) {
                this.currentUser = await response.json();
                this.showMainApp();
                this.updateUserInfo();
                this.loadEstablishments();
                this.loadMyOrders();
                this.startAutoRefresh();
            } else {
                this.logout();
            }
        } catch (error) {
            this.logout();
        }
    }

    logout() {
        this.token = null;
        this.currentUser = null;
        localStorage.removeItem('token');
        this.stopAutoRefresh();
        this.showAuthScreen();
    }

    startAutoRefresh() {
        // Clear any existing interval first
        this.stopAutoRefresh();
        
        // Set up auto-refresh every 10 seconds
        this.refreshInterval = setInterval(() => {
            if (this.currentUser) {
                console.log('Auto-refreshing orders...');
                this.loadMyOrders();
                // Also refresh deliveries if we're on that tab
                if (document.getElementById('myDeliveriesTab').classList.contains('border-temple-red')) {
                    this.loadMyDeliveries();
                }
            }
        }, 10000);
        
        console.log('Auto-refresh started (10 second intervals)');
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            console.log('Auto-refresh stopped');
        }
    }

    // UI Navigation Methods
    showAuthScreen() {
        document.getElementById('authScreen').classList.remove('hidden');
        document.getElementById('mainApp').classList.add('hidden');
        document.getElementById('navbar').classList.add('hidden');
    }

    showMainApp() {
        document.getElementById('authScreen').classList.add('hidden');
        document.getElementById('mainApp').classList.remove('hidden');
        document.getElementById('navbar').classList.remove('hidden');
    }

    showLoginForm(e) {
        if (e) e.preventDefault();
        document.getElementById('loginForm').classList.remove('hidden');
        document.getElementById('registerForm').classList.add('hidden');
    }

    showRegisterForm(e) {
        if (e) e.preventDefault();
        document.getElementById('loginForm').classList.add('hidden');
        document.getElementById('registerForm').classList.remove('hidden');
    }

    showTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active', 'border-temple-red', 'text-temple-red');
            btn.classList.add('border-transparent', 'text-gray-500');
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });

        if (tabName === 'request') {
            document.getElementById('requestTab').classList.add('active', 'border-temple-red', 'text-temple-red');
            document.getElementById('requestTab').classList.remove('border-transparent', 'text-gray-500');
            document.getElementById('requestContent').classList.remove('hidden');
        } else if (tabName === 'deliver') {
            document.getElementById('deliverTab').classList.add('active', 'border-temple-red', 'text-temple-red');
            document.getElementById('deliverTab').classList.remove('border-transparent', 'text-gray-500');
            document.getElementById('deliverContent').classList.remove('hidden');
            this.loadAvailableOrders();
            this.loadMyDeliveries();
        }
    }

    updateUserInfo() {
        if (this.currentUser) {
            document.getElementById('username').textContent = this.currentUser.username;
            document.getElementById('userPoints').textContent = this.currentUser.points;
        }
    }

    // Location Methods
    getUserLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.currentLocation = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };
                    this.loadEstablishments();
                    this.showAlert('Location updated!', 'success');
                },
                (error) => {
                    this.showAlert('Could not get your location', 'error');
                }
            );
        } else {
            this.showAlert('Geolocation is not supported by this browser', 'error');
        }
    }

    // Establishments Methods
    async loadEstablishments() {
        try {
            let url = `${this.baseURL}/establishments/`;
            if (this.currentLocation) {
                url += `?lat=${this.currentLocation.latitude}&lon=${this.currentLocation.longitude}`;
            }

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            });

            if (response.ok) {
                const establishments = await response.json();
                this.renderEstablishments(establishments);
            } else {
                const errorData = await response.json();
                console.error('Failed to load establishments:', errorData);
                this.showAlert(`Failed to load establishments: ${errorData.detail || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            console.error('Network error loading establishments:', error);
            this.showAlert('Failed to load establishments - network error', 'error');
        }
    }

    async searchEstablishments(query) {
        if (!query.trim()) {
            this.loadEstablishments();
            return;
        }

        try {
            let url = `${this.baseURL}/establishments/search?query=${encodeURIComponent(query)}`;
            if (this.currentLocation) {
                url += `&lat=${this.currentLocation.latitude}&lon=${this.currentLocation.longitude}`;
            }

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            });

            if (response.ok) {
                const establishments = await response.json();
                this.renderEstablishments(establishments);
            }
        } catch (error) {
            this.showAlert('Search failed', 'error');
        }
    }

    renderEstablishments(establishments) {
        const container = document.getElementById('establishmentsList');
        container.innerHTML = '';

        establishments.forEach(establishment => {
            const distanceText = establishment.distance ? 
                `<span class="text-gray-500 text-sm">${establishment.distance.toFixed(1)} miles away</span>` : '';

            const establishmentElement = document.createElement('div');
            establishmentElement.className = 'bg-white rounded-lg shadow-md p-4 cursor-pointer hover:shadow-lg transition-shadow';
            establishmentElement.innerHTML = `
                <div class="flex items-center space-x-4">
                    <img src="${establishment.image_url}" alt="${establishment.name}" 
                         class="w-16 h-16 rounded-lg object-cover">
                    <div class="flex-1">
                        <h3 class="font-bold text-lg">${establishment.name}</h3>
                        <p class="text-gray-600">${establishment.category}</p>
                        <p class="text-sm text-gray-500">${establishment.location.address}</p>
                        ${distanceText}
                    </div>
                    <i class="fas fa-chevron-right text-gray-400"></i>
                </div>
            `;

            establishmentElement.addEventListener('click', () => this.selectEstablishment(establishment));
            container.appendChild(establishmentElement);
        });
    }

    selectEstablishment(establishment) {
        this.selectedEstablishment = establishment;
        this.orderItems = [];
        this.renderOrderSidebar();
        document.getElementById('selectedEstablishmentName').textContent = establishment.name;
        document.getElementById('orderSidebar').classList.remove('hidden');
    }

    // Order Management Methods
    addOrderItem() {
        const name = document.getElementById('itemName').value.trim();
        const quantity = parseInt(document.getElementById('itemQuantity').value) || 1;
        const price = parseFloat(document.getElementById('itemPrice').value) || 0;
        const notes = document.getElementById('itemNotes').value.trim();

        if (!name || price <= 0) {
            this.showAlert('Please enter valid item details', 'error');
            return;
        }

        const item = { name, quantity, price, notes };
        this.orderItems.push(item);

        // Clear form
        document.getElementById('itemName').value = '';
        document.getElementById('itemQuantity').value = '1';
        document.getElementById('itemPrice').value = '';
        document.getElementById('itemNotes').value = '';

        this.renderOrderSidebar();
    }

    renderOrderSidebar() {
        const container = document.getElementById('orderItems');
        container.innerHTML = '';

        let subtotal = 0;

        this.orderItems.forEach((item, index) => {
            const itemTotal = item.quantity * item.price;
            subtotal += itemTotal;

            const itemElement = document.createElement('div');
            itemElement.className = 'flex justify-between items-start bg-gray-50 p-3 rounded';
            itemElement.innerHTML = `
                <div class="flex-1">
                    <div class="font-medium">${item.name}</div>
                    <div class="text-sm text-gray-600">Qty: ${item.quantity} × $${item.price.toFixed(2)}</div>
                    ${item.notes ? `<div class="text-sm text-gray-500">${item.notes}</div>` : ''}
                </div>
                <div class="text-right">
                    <div class="font-medium">$${itemTotal.toFixed(2)}</div>
                    <button class="text-red-500 hover:text-red-700 text-sm" onclick="app.removeOrderItem(${index})">
                        Remove
                    </button>
                </div>
            `;
            container.appendChild(itemElement);
        });

        // Update totals
        document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
        
        // Calculate delivery points (example: 10 points + 5% of subtotal)
        const deliveryPoints = Math.ceil(10 + (subtotal * 0.05));
        document.getElementById('deliveryPoints').textContent = deliveryPoints;

        // Enable/disable request button
        const requestBtn = document.getElementById('requestDeliveryBtn');
        const hasItems = this.orderItems.length > 0;
        const hasAddress = document.getElementById('deliveryAddress').value.trim() !== '';
        
        requestBtn.disabled = !hasItems || !hasAddress;
    }

    removeOrderItem(index) {
        this.orderItems.splice(index, 1);
        this.renderOrderSidebar();
    }

    async requestDelivery() {
        const deliveryAddress = document.getElementById('deliveryAddress').value.trim();
        const specialInstructions = document.getElementById('specialInstructions').value.trim();
        const deliveryPoints = parseInt(document.getElementById('deliveryPoints').textContent);

        if (!deliveryAddress) {
            this.showAlert('Please enter a delivery address', 'error');
            return;
        }

        if (this.orderItems.length === 0) {
            this.showAlert('Please add items to your order', 'error');
            return;
        }

        if (this.currentUser.points < deliveryPoints) {
            this.showAlert('Insufficient points for this delivery', 'error');
            return;
        }

        if (!this.selectedEstablishment) {
            this.showAlert('Please select a restaurant first', 'error');
            return;
        }

        try {
            this.showLoading(true);

            // Debug log to see establishment structure
            console.log('Selected establishment:', this.selectedEstablishment);
            
            const establishmentId = this.selectedEstablishment._id || this.selectedEstablishment.id;
            console.log('Using establishment ID:', establishmentId);
            
            if (!establishmentId) {
                this.showAlert('Invalid establishment selected', 'error');
                return;
            }

            const orderData = {
                establishment_id: establishmentId,
                items: this.orderItems,
                delivery_location: {
                    latitude: this.currentLocation ? this.currentLocation.latitude : 39.9811,
                    longitude: this.currentLocation ? this.currentLocation.longitude : -75.1540,
                    address: deliveryAddress
                },
                special_instructions: specialInstructions,
                delivery_points: deliveryPoints
            };

            const response = await fetch(`${this.baseURL}/orders/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`,
                },
                body: JSON.stringify(orderData),
            });

            if (response.ok) {
                this.showAlert('Order placed successfully!', 'success');
                this.resetOrderForm();
                this.loadMyOrders();
                await this.loadCurrentUser(); // Refresh user points
            } else {
                const error = await response.json();
                console.error('Order placement failed:', error);
                this.showAlert(error.detail || 'Failed to place order', 'error');
            }
        } catch (error) {
            console.error('Network error placing order:', error);
            this.showAlert('Failed to place order - network error', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    resetOrderForm() {
        this.selectedEstablishment = null;
        this.orderItems = [];
        document.getElementById('orderSidebar').classList.add('hidden');
        document.getElementById('deliveryAddress').value = '';
        document.getElementById('specialInstructions').value = '';
    }

    // Orders Display Methods
    async loadMyOrders() {
        try {
            const response = await fetch(`${this.baseURL}/orders/my-orders`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            });

            if (response.ok) {
                const orders = await response.json();
                this.renderMyOrders(orders);
            }
        } catch (error) {
            this.showAlert('Failed to load orders', 'error');
        }
    }

    renderMyOrders(orders) {
        const container = document.getElementById('myOrdersList');
        container.innerHTML = '';

        if (orders.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-8">No orders yet</p>';
            return;
        }

        orders.forEach(order => {
            this.renderOrderCard(container, order, true);
        });
    }

    async loadAvailableOrders() {
        try {
            const response = await fetch(`${this.baseURL}/orders/available`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            });

            if (response.ok) {
                const orders = await response.json();
                this.renderAvailableOrders(orders);
            }
        } catch (error) {
            this.showAlert('Failed to load available orders', 'error');
        }
    }

    renderAvailableOrders(orders) {
        const container = document.getElementById('availableOrdersList');
        container.innerHTML = '';

        if (orders.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-8">No orders available</p>';
            return;
        }

        orders.forEach(order => {
            this.renderOrderCard(container, order, false, true);
        });
    }

    async loadMyDeliveries() {
        try {
            const response = await fetch(`${this.baseURL}/orders/delivering`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            });

            if (response.ok) {
                const orders = await response.json();
                this.renderMyDeliveries(orders);
            }
        } catch (error) {
            this.showAlert('Failed to load deliveries', 'error');
        }
    }

    renderMyDeliveries(orders) {
        const container = document.getElementById('myDeliveriesList');
        container.innerHTML = '';

        if (orders.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-8">No active deliveries</p>';
            return;
        }

        orders.forEach(order => {
            this.renderOrderCard(container, order, false, false, true);
        });
    }

    renderOrderCard(container, order, isMyOrder = false, isAvailable = false, isMyDelivery = false) {
        const statusColors = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'accepted': 'bg-blue-100 text-blue-800',
            'picked_up': 'bg-purple-100 text-purple-800',
            'delivered': 'bg-green-100 text-green-800',
            'completed': 'bg-gray-100 text-gray-800',
            'cancelled': 'bg-red-100 text-red-800'
        };

        const orderElement = document.createElement('div');
        orderElement.className = 'bg-white rounded-lg shadow-md p-6';

        const itemsList = order.items.map(item => 
            `<li>${item.quantity}x ${item.name} ($${item.price.toFixed(2)})</li>`
        ).join('');

        let actionButtons = '';
        
        if (isAvailable) {
            actionButtons = `
                <button onclick="app.acceptOrder('${order._id}')" 
                    class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md">
                    Accept Order (+${order.delivery_points} points)
                </button>
            `;
        } else if (isMyDelivery) {
            if (order.status === 'accepted') {
                actionButtons = `
                    <button onclick="app.updateOrderStatus('${order._id}', 'picked_up')" 
                        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md mr-2">
                        Mark as Picked Up
                    </button>
                `;
            } else if (order.status === 'picked_up') {
                actionButtons = `
                    <input type="file" id="completionImage-${order._id}" accept="image/*" class="hidden">
                    <button onclick="document.getElementById('completionImage-${order._id}').click()" 
                        class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md mr-2">
                        Upload Photo & Complete
                    </button>
                `;
                
                // Add event listener for file upload
                setTimeout(() => {
                    const fileInput = document.getElementById(`completionImage-${order._id}`);
                    if (fileInput) {
                        fileInput.addEventListener('change', (e) => {
                            if (e.target.files[0]) {
                                this.uploadCompletionImage(order._id, e.target.files[0]);
                            }
                        });
                    }
                }, 100);
            }
        } else if (isMyOrder && order.status === 'delivered' && order.completion_image_url) {
            console.log('DEBUG: Showing completion button with photo for order:', order._id);
            actionButtons = `
                <button onclick="app.viewCompletionImage('${order.completion_image_url}')" 
                    class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md mr-2">
                    View Photo
                </button>
                <button onclick="app.completeOrder('${order._id}')" 
                    class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md">
                    Confirm Received
                </button>
            `;
        } else if (isMyOrder && order.status === 'delivered') {
            // Show complete button even without image for testing
            console.log('DEBUG: Showing completion button without photo for order:', order._id);
            actionButtons = `
                <button onclick="app.completeOrder('${order._id}')" 
                    class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md">
                    Confirm Received (No Photo)
                </button>
            `;
        } else if (isMyOrder) {
            // Debug: Show what status we have
            console.log('DEBUG: My order with status:', order.status, 'Order:', order._id);
            actionButtons = `
                <div class="text-sm text-gray-600">
                    Order Status: ${order.status} | My Order: ${isMyOrder} | Has Photo: ${!!order.completion_image_url}
                    <br>Order ID: ${order._id}
                </div>
            `;
        }

        orderElement.innerHTML = `
            <div class="flex justify-between items-start mb-4">
                <div>
                    <span class="px-2 py-1 rounded-full text-xs font-medium ${statusColors[order.status]}">
                        ${order.status.replace('_', ' ').toUpperCase()}
                    </span>
                    <div class="text-sm text-gray-500 mt-1">
                        Order #${order._id.slice(-8)}
                    </div>
                </div>
                <div class="text-right">
                    <div class="font-bold text-temple-red">${order.delivery_points} points</div>
                    <div class="text-sm text-gray-500">
                        ${new Date(order.created_at).toLocaleDateString()}
                    </div>
                </div>
            </div>
            
            <div class="mb-4">
                <h4 class="font-semibold mb-2">Items:</h4>
                <ul class="list-disc list-inside text-sm text-gray-700">
                    ${itemsList}
                </ul>
            </div>
            
            <div class="mb-4">
                <div class="text-sm">
                    <strong>Delivery to:</strong> ${order.delivery_location.address}
                </div>
                ${order.special_instructions ? 
                    `<div class="text-sm mt-1"><strong>Instructions:</strong> ${order.special_instructions}</div>` : ''
                }
            </div>
            
            ${actionButtons ? `<div class="mt-4">${actionButtons}</div>` : ''}
        `;

        container.appendChild(orderElement);
    }

    // Order Actions
    async acceptOrder(orderId) {
        try {
            this.showLoading(true);
            const response = await fetch(`${this.baseURL}/orders/${orderId}/accept`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            });

            if (response.ok) {
                this.showAlert('Order accepted!', 'success');
                this.loadAvailableOrders();
                this.loadMyDeliveries();
            } else {
                const error = await response.json();
                this.showAlert(error.detail || 'Failed to accept order', 'error');
            }
        } catch (error) {
            this.showAlert('Failed to accept order', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async updateOrderStatus(orderId, status) {
        try {
            this.showLoading(true);
            const response = await fetch(`${this.baseURL}/orders/${orderId}/update-status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`,
                },
                body: JSON.stringify({ status }),
            });

            if (response.ok) {
                this.showAlert('Status updated!', 'success');
                this.loadMyDeliveries();
            } else {
                const error = await response.json();
                this.showAlert(error.detail || 'Failed to update status', 'error');
            }
        } catch (error) {
            this.showAlert('Failed to update status', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async uploadCompletionImage(orderId, file) {
        try {
            this.showLoading(true);
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${this.baseURL}/orders/${orderId}/upload-image`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
                body: formData,
            });

            if (response.ok) {
                this.showAlert('Photo uploaded and order marked as delivered!', 'success');
                this.loadMyDeliveries();
            } else {
                const error = await response.json();
                this.showAlert(error.detail || 'Failed to upload photo', 'error');
            }
        } catch (error) {
            this.showAlert('Failed to upload photo', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async completeOrder(orderId) {
        console.log('DEBUG: completeOrder called for order:', orderId);
        try {
            this.showLoading(true);
            const response = await fetch(`${this.baseURL}/orders/${orderId}/complete`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            });

            console.log('DEBUG: Complete order response status:', response.status);
            
            if (response.ok) {
                const result = await response.json();
                console.log('DEBUG: Complete order success:', result);
                this.showAlert('Order completed! Points transferred.', 'success');
                this.loadMyOrders();
                await this.loadCurrentUser(); // Refresh user points
            } else {
                const error = await response.json();
                console.log('DEBUG: Complete order error:', error);
                this.showAlert(error.detail || 'Failed to complete order', 'error');
            }
        } catch (error) {
            console.log('DEBUG: Complete order exception:', error);
            this.showAlert('Failed to complete order', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    viewCompletionImage(imageUrl) {
        // Create modal to display the image
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white p-4 rounded-lg max-w-lg max-h-96">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-semibold">Delivery Confirmation Photo</h3>
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" 
                        class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <img src="${imageUrl}" alt="Delivery confirmation" class="max-w-full max-h-64 object-contain">
            </div>
        `;
        document.body.appendChild(modal);
    }

    // Utility Methods
    showLoading(show) {
        const spinner = document.getElementById('loadingSpinner');
        if (show) {
            spinner.classList.remove('hidden');
        } else {
            spinner.classList.add('hidden');
        }
    }

    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alertContainer');
        const alert = document.createElement('div');
        
        // Ensure message is a string
        let displayMessage = message;
        if (typeof message === 'object') {
            displayMessage = JSON.stringify(message);
        } else if (message === undefined || message === null) {
            displayMessage = 'Unknown error occurred';
        } else {
            displayMessage = String(message);
        }
        
        const colors = {
            'success': 'bg-green-500',
            'error': 'bg-red-500',
            'info': 'bg-blue-500'
        };

        alert.className = `${colors[type]} text-white px-6 py-3 rounded-md shadow-lg`;
        alert.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${displayMessage}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        alertContainer.appendChild(alert);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize the app
const app = new OwlHacksDeliveryApp();