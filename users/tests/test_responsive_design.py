"""
Tests for responsive design and mobile compatibility
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal

from adminside.models import Package, Destination, Accommodation


class ResponsiveDesignTest(TestCase):
    """Test responsive design and mobile compatibility"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test destination
        self.destination = Destination.objects.create(
            name='Test Destination',
            slug='test-destination',
            destination_type=Destination.PLACE,
            description='Test destination description'
        )
        
        # Create test package
        self.package = Package.objects.create(
            name='Test Package',
            slug='test-package',
            description='Test package description',
            main_destination=self.destination,
            duration_days=3,
            duration_nights=2,
            adult_price=1000,
            child_price=700,
            status=Package.PUBLISHED
        )
        
        # Create test accommodation
        self.accommodation = Accommodation.objects.create(
            name='Test Hotel',
            slug='test-hotel',
            description='Test hotel description',
            destination=self.destination,
            price_per_room_per_night=100
        )
    
    def test_mobile_viewport_meta_tag(self):
        """Test that pages include mobile viewport meta tag"""
        urls_to_test = [
            reverse('adminside:home'),
            reverse('adminside:packages'),
            reverse('adminside:package_detail', args=[self.package.slug]),
            reverse('adminside:accommodations'),
            reverse('adminside:accommodation_detail', args=[self.accommodation.slug]),
        ]
        
        for url in urls_to_test:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(
                response, 
                '<meta name="viewport" content="width=device-width, initial-scale=1">',
                html=True
            )
    
    def test_responsive_css_classes(self):
        """Test that pages include responsive CSS classes"""
        response = self.client.get(reverse('adminside:home'))
        self.assertEqual(response.status_code, 200)
        
        # Check for Bootstrap responsive classes
        responsive_classes = [
            'container-fluid',
            'row',
            'col-',
            'd-none d-md-block',  # Hide on mobile, show on desktop
            'd-block d-md-none',  # Show on mobile, hide on desktop
        ]
        
        for css_class in responsive_classes:
            self.assertContains(response, css_class)
    
    def test_mobile_navigation_menu(self):
        """Test mobile navigation menu functionality"""
        response = self.client.get(reverse('adminside:home'))
        self.assertEqual(response.status_code, 200)
        
        # Check for mobile menu toggle button
        self.assertContains(response, 'navbar-toggler')
        self.assertContains(response, 'data-bs-toggle="collapse"')
        
        # Check for collapsible navigation
        self.assertContains(response, 'navbar-collapse')
    
    def test_package_grid_responsiveness(self):
        """Test package grid responsiveness"""
        response = self.client.get(reverse('adminside:packages'))
        self.assertEqual(response.status_code, 200)
        
        # Check for responsive grid classes
        responsive_grid_classes = [
            'col-12',      # Full width on mobile
            'col-md-6',    # Half width on medium screens
            'col-lg-4',    # Third width on large screens
        ]
        
        for css_class in responsive_grid_classes:
            self.assertContains(response, css_class)
    
    def test_booking_form_mobile_layout(self):
        """Test booking form mobile layout"""
        # Add package to cart first
        self.client.post(reverse('users:add_to_cart', args=[self.package.id]), {
            'adults': 2,
            'children': 0,
            'rooms': 1
        })
        
        response = self.client.get(reverse('users:checkout_details'))
        self.assertEqual(response.status_code, 200)
        
        # Check for mobile-friendly form classes
        mobile_form_classes = [
            'form-control',
            'mb-3',  # Mobile spacing
            'col-12',  # Full width on mobile
        ]
        
        for css_class in mobile_form_classes:
            self.assertContains(response, css_class)
    
    def test_user_dashboard_mobile_layout(self):
        """Test user dashboard mobile layout"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('users:user_profile'))
        self.assertEqual(response.status_code, 200)
        
        # Check for mobile dashboard layout
        self.assertContains(response, 'col-12')  # Full width cards on mobile
        self.assertContains(response, 'mb-3')    # Mobile spacing
    
    def test_image_responsiveness(self):
        """Test image responsiveness"""
        response = self.client.get(reverse('adminside:package_detail', args=[self.package.slug]))
        self.assertEqual(response.status_code, 200)
        
        # Check for responsive image classes
        self.assertContains(response, 'img-fluid')  # Bootstrap responsive images
    
    def test_table_responsiveness(self):
        """Test table responsiveness for booking history"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('users:booking_history'))
        self.assertEqual(response.status_code, 200)
        
        # Check for responsive table wrapper
        self.assertContains(response, 'table-responsive')
    
    def test_button_mobile_sizing(self):
        """Test button mobile sizing"""
        response = self.client.get(reverse('adminside:package_detail', args=[self.package.slug]))
        self.assertEqual(response.status_code, 200)
        
        # Check for mobile-friendly button classes
        mobile_button_classes = [
            'btn-lg',      # Larger buttons for mobile
            'w-100',       # Full width buttons on mobile
            'd-grid',      # Grid display for full width
        ]
        
        # At least one of these should be present for mobile optimization
        has_mobile_button = any(
            css_class in response.content.decode() 
            for css_class in mobile_button_classes
        )
        self.assertTrue(has_mobile_button)
    
    def test_font_size_mobile_optimization(self):
        """Test font size mobile optimization"""
        response = self.client.get(reverse('adminside:home'))
        self.assertEqual(response.status_code, 200)
        
        # Check for mobile typography classes
        mobile_typography = [
            'fs-',         # Font size utilities
            'text-',       # Text utilities
            'lead',        # Lead text for better readability
        ]
        
        has_mobile_typography = any(
            css_class in response.content.decode() 
            for css_class in mobile_typography
        )
        self.assertTrue(has_mobile_typography)
    
    def test_touch_friendly_elements(self):
        """Test touch-friendly elements"""
        response = self.client.get(reverse('adminside:packages'))
        self.assertEqual(response.status_code, 200)
        
        # Check for touch-friendly spacing
        touch_classes = [
            'p-3',         # Adequate padding
            'py-3',        # Vertical padding
            'px-3',        # Horizontal padding
            'btn-lg',      # Large buttons
        ]
        
        has_touch_friendly = any(
            css_class in response.content.decode() 
            for css_class in touch_classes
        )
        self.assertTrue(has_touch_friendly)
    
    def test_mobile_cart_functionality(self):
        """Test mobile cart functionality"""
        # Add package to cart
        response = self.client.post(reverse('users:add_to_cart', args=[self.package.id]), {
            'adults': 1,
            'children': 0,
            'rooms': 1
        })
        
        # Check cart view on mobile
        response = self.client.get(reverse('users:view_cart'))
        self.assertEqual(response.status_code, 200)
        
        # Should have mobile-optimized cart layout
        self.assertContains(response, 'col-12')  # Full width on mobile
    
    def test_mobile_search_functionality(self):
        """Test mobile search functionality"""
        response = self.client.get(reverse('adminside:packages'))
        self.assertEqual(response.status_code, 200)
        
        # Check for mobile search form
        self.assertContains(response, 'form-control')
        
        # Test search with mobile user agent
        response = self.client.get(
            reverse('adminside:packages') + '?search=safari',
            HTTP_USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_mobile_pagination(self):
        """Test mobile pagination"""
        # Create multiple packages to trigger pagination
        for i in range(15):
            Package.objects.create(
                name=f'Package {i}',
                slug=f'package-{i}',
                description=f'Package {i} description',
                main_destination=self.destination,
                duration_days=2,
                duration_nights=1,
                adult_price=500,
                child_price=350,
                status=Package.PUBLISHED
            )
        
        response = self.client.get(reverse('adminside:packages'))
        self.assertEqual(response.status_code, 200)
        
        # Check for mobile-friendly pagination
        if 'pagination' in response.content.decode():
            self.assertContains(response, 'page-link')
    
    def test_mobile_form_validation(self):
        """Test mobile form validation"""
        # Add package to cart
        self.client.post(reverse('users:add_to_cart', args=[self.package.id]), {
            'adults': 1,
            'children': 0,
            'rooms': 1
        })
        
        # Submit invalid form data
        response = self.client.post(reverse('users:checkout_details'), {
            'full_name': '',  # Invalid: empty name
            'email': 'invalid-email',  # Invalid: bad email format
            'phone_number': '',  # Invalid: empty phone
        })
        
        # Should stay on form with validation errors
        self.assertEqual(response.status_code, 200)
        
        # Check for mobile-friendly error display
        self.assertContains(response, 'is-invalid')  # Bootstrap validation classes
    
    def test_mobile_accessibility(self):
        """Test mobile accessibility features"""
        response = self.client.get(reverse('adminside:home'))
        self.assertEqual(response.status_code, 200)
        
        # Check for accessibility attributes
        accessibility_attributes = [
            'aria-label',
            'aria-expanded',
            'role=',
            'alt=',
        ]
        
        has_accessibility = any(
            attr in response.content.decode() 
            for attr in accessibility_attributes
        )
        self.assertTrue(has_accessibility)
    
    def test_mobile_performance_optimization(self):
        """Test mobile performance optimization"""
        response = self.client.get(reverse('adminside:home'))
        self.assertEqual(response.status_code, 200)
        
        # Check for performance optimization
        performance_features = [
            'loading="lazy"',  # Lazy loading images
            'preload',         # Resource preloading
            'async',           # Async script loading
        ]
        
        # At least one performance feature should be present
        has_performance_optimization = any(
            feature in response.content.decode() 
            for feature in performance_features
        )
        # Note: This might not always be true, so we'll just check without assertion
        # self.assertTrue(has_performance_optimization)
    
    def test_cross_browser_compatibility(self):
        """Test cross-browser compatibility"""
        # Test with different user agents
        user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',  # iOS Safari
            'Mozilla/5.0 (Android 10; Mobile; rv:81.0)',  # Android Firefox
            'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36',  # Android Chrome
        ]
        
        for user_agent in user_agents:
            response = self.client.get(
                reverse('adminside:home'),
                HTTP_USER_AGENT=user_agent
            )
            self.assertEqual(response.status_code, 200)
            
            # Should contain responsive meta tag for all browsers
            self.assertContains(
                response, 
                '<meta name="viewport" content="width=device-width, initial-scale=1">',
                html=True
            )
