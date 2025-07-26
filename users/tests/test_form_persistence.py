"""
Tests for form data persistence functionality
"""

from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from datetime import datetime, date

from users.form_persistence import FormDataManager, get_form_manager
from users.checkout_forms import CheckoutForm


class FormDataManagerTest(TestCase):
    """Test FormDataManager functionality"""
    
    def setUp(self):
        """Set up test request with session"""
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        
        # Add session to request
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(self.request)
        self.request.session.save()
        
        self.form_manager = FormDataManager(self.request)
    
    def test_save_and_get_form_data(self):
        """Test saving and retrieving form data"""
        test_data = {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone_number': '+254701363551'
        }
        
        # Save data
        self.form_manager.save_form_data('details', test_data)
        
        # Retrieve data
        retrieved_data = self.form_manager.get_form_data('details')
        
        self.assertEqual(retrieved_data['full_name'], 'John Doe')
        self.assertEqual(retrieved_data['email'], 'john@example.com')
        self.assertEqual(retrieved_data['phone_number'], '+254701363551')
        self.assertIn('_timestamp', retrieved_data)
    
    def test_merge_form_data(self):
        """Test merging form data"""
        # Save initial data
        initial_data = {
            'full_name': 'John Doe',
            'email': 'john@example.com'
        }
        self.form_manager.save_form_data('details', initial_data)
        
        # Save additional data with merge=True (default)
        additional_data = {
            'phone_number': '+254701363551',
            'special_requests': 'Vegetarian meals'
        }
        self.form_manager.save_form_data('details', additional_data, merge=True)
        
        # Retrieve merged data
        merged_data = self.form_manager.get_form_data('details')
        
        self.assertEqual(merged_data['full_name'], 'John Doe')
        self.assertEqual(merged_data['email'], 'john@example.com')
        self.assertEqual(merged_data['phone_number'], '+254701363551')
        self.assertEqual(merged_data['special_requests'], 'Vegetarian meals')
    
    def test_replace_form_data(self):
        """Test replacing form data"""
        # Save initial data
        initial_data = {
            'full_name': 'John Doe',
            'email': 'john@example.com'
        }
        self.form_manager.save_form_data('details', initial_data)
        
        # Replace with new data
        new_data = {
            'full_name': 'Jane Smith',
            'phone_number': '+254701363552'
        }
        self.form_manager.save_form_data('details', new_data, merge=False)
        
        # Retrieve replaced data
        replaced_data = self.form_manager.get_form_data('details')
        
        self.assertEqual(replaced_data['full_name'], 'Jane Smith')
        self.assertEqual(replaced_data['phone_number'], '+254701363552')
        self.assertNotIn('email', replaced_data)  # Should be removed
    
    def test_clear_form_data(self):
        """Test clearing form data"""
        # Save data for multiple steps
        self.form_manager.save_form_data('package_selection', {'package_id': 1})
        self.form_manager.save_form_data('customization', {'accommodations': [1, 2]})
        self.form_manager.save_form_data('details', {'full_name': 'John Doe'})
        
        # Clear specific step
        self.form_manager.clear_form_data('details')
        
        # Check that only details step was cleared
        self.assertEqual(self.form_manager.get_form_data('details'), {})
        self.assertNotEqual(self.form_manager.get_form_data('package_selection'), {})
        self.assertNotEqual(self.form_manager.get_form_data('customization'), {})
        
        # Clear all data
        self.form_manager.clear_form_data()
        
        # Check that all data is cleared
        self.assertEqual(self.form_manager.get_form_data('package_selection'), {})
        self.assertEqual(self.form_manager.get_form_data('customization'), {})
        self.assertEqual(self.form_manager.get_form_data('details'), {})
    
    def test_has_form_data(self):
        """Test checking if form data exists"""
        # Initially no data
        self.assertFalse(self.form_manager.has_form_data())
        self.assertFalse(self.form_manager.has_form_data('details'))
        
        # Save some data
        self.form_manager.save_form_data('details', {'full_name': 'John Doe'})
        
        # Check data exists
        self.assertTrue(self.form_manager.has_form_data())
        self.assertTrue(self.form_manager.has_form_data('details'))
        self.assertFalse(self.form_manager.has_form_data('customization'))
    
    def test_get_step_progress(self):
        """Test getting step progress"""
        # Save data for multiple steps
        self.form_manager.save_form_data('package_selection', {'package_id': 1})
        self.form_manager.save_form_data('customization', {'accommodations': [1]})
        self.form_manager.save_form_data('details', {'full_name': 'John Doe'})
        
        progress = self.form_manager.get_step_progress()
        
        self.assertIn('package_selection', progress)
        self.assertIn('customization', progress)
        self.assertIn('details', progress)
        self.assertEqual(len(progress), 3)
    
    def test_validate_step_completion(self):
        """Test step completion validation"""
        # Test package selection validation
        self.assertFalse(self.form_manager.validate_step_completion('package_selection'))
        
        self.form_manager.save_form_data('package_selection', {
            'package_id': 1,
            'adults': 2
        })
        self.assertTrue(self.form_manager.validate_step_completion('package_selection'))
        
        # Test details validation
        self.assertFalse(self.form_manager.validate_step_completion('details'))
        
        self.form_manager.save_form_data('details', {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone_number': '+254701363551'
        })
        self.assertTrue(self.form_manager.validate_step_completion('details'))
        
        # Test customization validation (always true as it's optional)
        self.assertTrue(self.form_manager.validate_step_completion('customization'))
    
    def test_get_form_initial_data(self):
        """Test getting initial data for forms"""
        # Save form data with date
        form_data = {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'travel_date': date.today().isoformat(),
            'special_requests': 'Test request'
        }
        self.form_manager.save_form_data('details', form_data)
        
        # Get initial data
        initial_data = self.form_manager.get_form_initial_data('details')
        
        self.assertEqual(initial_data['full_name'], 'John Doe')
        self.assertEqual(initial_data['email'], 'john@example.com')
        self.assertEqual(initial_data['special_requests'], 'Test request')
        
        # Check date conversion
        self.assertIsInstance(initial_data['travel_date'], date)
        
        # Test with form class filtering
        initial_data_filtered = self.form_manager.get_form_initial_data('details', CheckoutForm)
        
        # Should only include fields that exist in CheckoutForm
        self.assertIn('full_name', initial_data_filtered)
        self.assertIn('email', initial_data_filtered)
        # Internal fields should be excluded
        self.assertNotIn('_timestamp', initial_data_filtered)
    
    def test_save_form_instance_data(self):
        """Test saving data from form instance"""
        # Create a form with valid data
        form_data = {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone_number': '+254701363551',
            'travel_date': date.today(),
            'special_requests': 'Test request',
            'terms_accepted': True,
            'marketing_consent': False
        }
        
        form = CheckoutForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Save form instance data
        self.form_manager.save_form_instance_data('details', form)
        
        # Retrieve and verify
        saved_data = self.form_manager.get_form_data('details')
        
        self.assertEqual(saved_data['full_name'], 'John Doe')
        self.assertEqual(saved_data['email'], 'john@example.com')
        self.assertEqual(saved_data['phone_number'], '+254701363551')
        self.assertEqual(saved_data['special_requests'], 'Test request')
        self.assertTrue(saved_data['terms_accepted'])
        self.assertFalse(saved_data['marketing_consent'])
        
        # Date should be converted to ISO string
        self.assertEqual(saved_data['travel_date'], date.today().isoformat())
    
    def test_get_booking_summary(self):
        """Test getting booking summary"""
        # Save data for all steps
        self.form_manager.save_form_data('package_selection', {
            'package_id': 1,
            'adults': 2,
            'children': 1
        })
        
        self.form_manager.save_form_data('customization', {
            'accommodations': [1, 2],
            'travel_modes': [1],
            'self_drive': False
        })
        
        self.form_manager.save_form_data('details', {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone_number': '+254701363551'
        })
        
        # Get summary
        summary = self.form_manager.get_booking_summary()
        
        self.assertIn('package', summary)
        self.assertIn('customization', summary)
        self.assertIn('customer', summary)
        
        self.assertEqual(summary['package']['package_id'], 1)
        self.assertEqual(summary['package']['adults'], 2)
        self.assertEqual(summary['customization']['accommodations'], [1, 2])
        self.assertEqual(summary['customer']['full_name'], 'John Doe')
    
    def test_export_for_booking(self):
        """Test exporting data for booking creation"""
        # Save data for multiple steps
        self.form_manager.save_form_data('package_selection', {
            'package_id': 1,
            'adults': 2
        })
        
        self.form_manager.save_form_data('details', {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            '_timestamp': datetime.now().isoformat()  # Internal field
        })
        
        # Export for booking
        booking_data = self.form_manager.export_for_booking()
        
        # Should flatten all data and exclude internal fields
        self.assertEqual(booking_data['package_id'], 1)
        self.assertEqual(booking_data['adults'], 2)
        self.assertEqual(booking_data['full_name'], 'John Doe')
        self.assertEqual(booking_data['email'], 'john@example.com')
        self.assertNotIn('_timestamp', booking_data)
    
    def test_get_form_manager_convenience_function(self):
        """Test the convenience function for getting FormDataManager"""
        manager = get_form_manager(self.request)
        self.assertIsInstance(manager, FormDataManager)
        
        # Test that it works the same as direct instantiation
        manager.save_form_data('test', {'key': 'value'})
        direct_manager = FormDataManager(self.request)
        
        self.assertEqual(
            manager.get_form_data('test'),
            direct_manager.get_form_data('test')
        )


class FormPersistenceIntegrationTest(TestCase):
    """Integration tests for form persistence in views"""
    
    def setUp(self):
        """Set up test client"""
        self.client = self.client_class()
    
    def test_form_persistence_across_requests(self):
        """Test that form data persists across multiple requests"""
        # Make initial request to save some data
        session = self.client.session
        session['booking_form_data'] = {
            'details': {
                'full_name': 'Test User',
                'email': 'test@example.com',
                '_timestamp': datetime.now().isoformat()
            }
        }
        session.save()
        
        # Make another request and check if data persists
        response = self.client.get('/profile/')  # Any URL that uses sessions
        
        # Check that session data is still there
        updated_session = self.client.session
        self.assertIn('booking_form_data', updated_session)
        self.assertEqual(
            updated_session['booking_form_data']['details']['full_name'],
            'Test User'
        )
    
    def test_session_cleanup_after_booking(self):
        """Test that form data is cleaned up after successful booking"""
        # This would be tested in the booking flow integration tests
        # as it requires the full booking process
        pass
