"""
Tests for cart functionality
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal

from users.cart import Cart
from adminside.models import Package, Destination, Accommodation, TravelMode


class CartFunctionalityTest(TestCase):
    """Test cart operations and functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test destination
        self.destination = Destination.objects.create(
            name='Maasai Mara',
            slug='maasai-mara',
            destination_type=Destination.PLACE,
            description='Famous wildlife reserve'
        )
        
        # Create test package
        self.package = Package.objects.create(
            name='Maasai Mara Safari',
            slug='maasai-mara-safari',
            description='3-day wildlife safari',
            main_destination=self.destination,
            duration_days=3,
            duration_nights=2,
            adult_price=1500,
            child_price=1050,
            status=Package.PUBLISHED
        )
        
        # Create test accommodation
        self.accommodation = Accommodation.objects.create(
            name='Safari Lodge',
            slug='safari-lodge',
            description='Luxury safari lodge',
            destination=self.destination,
            price_per_room_per_night=200,
            is_active=True
        )
        
        # Create test travel mode
        self.travel_mode = TravelMode.objects.create(
            name='4WD Safari Vehicle',
            description='Comfortable safari vehicle',
            price_per_person=100,
            is_active=True
        )
        
        # Initialize cart
        self.cart = Cart(self.client)
    
    def test_cart_initialization(self):
        """Test cart initialization"""
        self.assertIsNotNone(self.cart.session)
        self.assertEqual(len(self.cart.get_cart_items()), 0)
    
    def test_add_package_to_cart(self):
        """Test adding package to cart"""
        self.cart.add_package(self.package, adults=2, children=1, rooms=1)
        
        cart_items = self.cart.get_cart_items()
        self.assertEqual(len(cart_items), 1)
        
        item = cart_items[0]
        self.assertEqual(item['package'], self.package)
        self.assertEqual(item['adults'], 2)
        self.assertEqual(item['children'], 1)
        self.assertEqual(item['rooms'], 1)
    
    def test_add_package_via_view(self):
        """Test adding package to cart via view"""
        response = self.client.post(reverse('users:add_to_cart', args=[self.package.id]), {
            'adults': 3,
            'children': 2,
            'rooms': 2
        })
        
        # Should redirect to customization page
        self.assertEqual(response.status_code, 302)
        
        # Check cart contents
        cart_items = self.cart.get_cart_items()
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0]['adults'], 3)
        self.assertEqual(cart_items[0]['children'], 2)
        self.assertEqual(cart_items[0]['rooms'], 2)
    
    def test_add_accommodation_to_cart(self):
        """Test adding accommodation to cart item"""
        # First add package
        self.cart.add_package(self.package, adults=2, children=0, rooms=1)
        
        # Then add accommodation
        self.cart.add_accommodation(self.package.id, self.accommodation.id)
        
        cart_items = self.cart.get_cart_items()
        self.assertEqual(len(cart_items), 1)
        self.assertIn(self.accommodation, cart_items[0]['accommodations'])
    
    def test_add_travel_mode_to_cart(self):
        """Test adding travel mode to cart item"""
        # First add package
        self.cart.add_package(self.package, adults=2, children=0, rooms=1)
        
        # Then add travel mode
        self.cart.add_travel_mode(self.package.id, self.travel_mode.id)
        
        cart_items = self.cart.get_cart_items()
        self.assertEqual(len(cart_items), 1)
        self.assertIn(self.travel_mode, cart_items[0]['travel_modes'])
    
    def test_remove_accommodation_from_cart(self):
        """Test removing accommodation from cart item"""
        # Add package and accommodation
        self.cart.add_package(self.package, adults=2, children=0, rooms=1)
        self.cart.add_accommodation(self.package.id, self.accommodation.id)
        
        # Verify accommodation is added
        cart_items = self.cart.get_cart_items()
        self.assertIn(self.accommodation, cart_items[0]['accommodations'])
        
        # Remove accommodation
        self.cart.remove_accommodation(self.package.id, self.accommodation.id)
        
        # Verify accommodation is removed
        cart_items = self.cart.get_cart_items()
        self.assertNotIn(self.accommodation, cart_items[0]['accommodations'])
    
    def test_remove_travel_mode_from_cart(self):
        """Test removing travel mode from cart item"""
        # Add package and travel mode
        self.cart.add_package(self.package, adults=2, children=0, rooms=1)
        self.cart.add_travel_mode(self.package.id, self.travel_mode.id)
        
        # Verify travel mode is added
        cart_items = self.cart.get_cart_items()
        self.assertIn(self.travel_mode, cart_items[0]['travel_modes'])
        
        # Remove travel mode
        self.cart.remove_travel_mode(self.package.id, self.travel_mode.id)
        
        # Verify travel mode is removed
        cart_items = self.cart.get_cart_items()
        self.assertNotIn(self.travel_mode, cart_items[0]['travel_modes'])
    
    def test_update_package_quantities(self):
        """Test updating package quantities in cart"""
        # Add package
        self.cart.add_package(self.package, adults=2, children=1, rooms=1)
        
        # Update quantities
        self.cart.update_package(self.package.id, adults=3, children=2, rooms=2)
        
        cart_items = self.cart.get_cart_items()
        item = cart_items[0]
        self.assertEqual(item['adults'], 3)
        self.assertEqual(item['children'], 2)
        self.assertEqual(item['rooms'], 2)
    
    def test_remove_package_from_cart(self):
        """Test removing package from cart"""
        # Add package
        self.cart.add_package(self.package, adults=2, children=0, rooms=1)
        
        # Verify package is in cart
        cart_items = self.cart.get_cart_items()
        self.assertEqual(len(cart_items), 1)
        
        # Remove package
        self.cart.remove_package(self.package.id)
        
        # Verify cart is empty
        cart_items = self.cart.get_cart_items()
        self.assertEqual(len(cart_items), 0)
    
    def test_clear_cart(self):
        """Test clearing entire cart"""
        # Add multiple items
        self.cart.add_package(self.package, adults=2, children=0, rooms=1)
        self.cart.add_accommodation(self.package.id, self.accommodation.id)
        self.cart.add_travel_mode(self.package.id, self.travel_mode.id)
        
        # Verify cart has items
        cart_items = self.cart.get_cart_items()
        self.assertEqual(len(cart_items), 1)
        self.assertIn(self.accommodation, cart_items[0]['accommodations'])
        self.assertIn(self.travel_mode, cart_items[0]['travel_modes'])
        
        # Clear cart
        self.cart.clear()
        
        # Verify cart is empty
        cart_items = self.cart.get_cart_items()
        self.assertEqual(len(cart_items), 0)
    
    def test_cart_total_calculation(self):
        """Test cart total calculation"""
        # Add package with specific quantities
        self.cart.add_package(self.package, adults=2, children=1, rooms=1)
        self.cart.add_accommodation(self.package.id, self.accommodation.id)
        self.cart.add_travel_mode(self.package.id, self.travel_mode.id)
        
        total = self.cart.get_total_price()
        
        # Expected calculation:
        # Package: 2 adults * $1500 + 1 child * $1050 = $4050
        # Accommodation: 1 room * $200/night * 2 nights = $400
        # Travel: (2 adults + 1 child) * $100 = $300
        # Total: $4050 + $400 + $300 = $4750
        expected_total = Decimal('4750.00')
        self.assertEqual(total, expected_total)
    
    def test_cart_item_count(self):
        """Test cart item count"""
        # Initially empty
        self.assertEqual(self.cart.get_item_count(), 0)
        
        # Add one package
        self.cart.add_package(self.package, adults=2, children=1, rooms=1)
        self.assertEqual(self.cart.get_item_count(), 1)
        
        # Add accommodations and travel modes (should still be 1 package)
        self.cart.add_accommodation(self.package.id, self.accommodation.id)
        self.cart.add_travel_mode(self.package.id, self.travel_mode.id)
        self.assertEqual(self.cart.get_item_count(), 1)
    
    def test_cart_persistence_across_requests(self):
        """Test that cart persists across requests"""
        # Add package in first request
        response = self.client.post(reverse('users:add_to_cart', args=[self.package.id]), {
            'adults': 2,
            'children': 0,
            'rooms': 1
        })
        
        # Make another request and check cart
        response = self.client.get(reverse('users:view_cart'))
        
        # Cart should still contain the package
        cart = Cart(self.client)
        cart_items = cart.get_cart_items()
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0]['package'], self.package)
    
    def test_cart_with_invalid_package(self):
        """Test cart behavior with invalid package ID"""
        # Try to add non-existent package
        try:
            self.cart.add_package(999, adults=1, children=0, rooms=1)
        except Package.DoesNotExist:
            pass  # Expected behavior
        
        # Cart should remain empty
        cart_items = self.cart.get_cart_items()
        self.assertEqual(len(cart_items), 0)
    
    def test_cart_with_invalid_accommodation(self):
        """Test cart behavior with invalid accommodation ID"""
        # Add valid package first
        self.cart.add_package(self.package, adults=1, children=0, rooms=1)
        
        # Try to add non-existent accommodation
        try:
            self.cart.add_accommodation(self.package.id, 999)
        except Accommodation.DoesNotExist:
            pass  # Expected behavior
        
        # Package should still be in cart, but no accommodations
        cart_items = self.cart.get_cart_items()
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(len(cart_items[0]['accommodations']), 0)
    
    def test_cart_session_management(self):
        """Test cart session management"""
        # Add package
        self.cart.add_package(self.package, adults=2, children=0, rooms=1)
        
        # Check session data
        session_data = self.client.session.get('cart', {})
        self.assertIn('items', session_data)
        self.assertEqual(len(session_data['items']), 1)
        
        # Clear cart
        self.cart.clear()
        
        # Check session is cleared
        session_data = self.client.session.get('cart', {})
        self.assertEqual(session_data.get('items', []), [])
    
    def test_cart_view_rendering(self):
        """Test cart view rendering"""
        # Add package to cart
        self.cart.add_package(self.package, adults=2, children=1, rooms=1)
        
        # Access cart view
        response = self.client.get(reverse('users:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.package.name)
        self.assertContains(response, '2 Adults')
        self.assertContains(response, '1 Child')
    
    def test_empty_cart_view(self):
        """Test empty cart view"""
        response = self.client.get(reverse('users:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your cart is empty')
    
    def test_cart_ajax_operations(self):
        """Test AJAX cart operations"""
        # Add package via AJAX
        response = self.client.post(
            reverse('users:add_to_cart', args=[self.package.id]),
            {
                'adults': 2,
                'children': 0,
                'rooms': 1
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should return JSON response for AJAX
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Check cart contents
        cart_items = self.cart.get_cart_items()
        self.assertEqual(len(cart_items), 1)
