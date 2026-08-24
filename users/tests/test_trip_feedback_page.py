from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from users.models import TripFeedback


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='test@novustelltravel.com',
    ADMIN_EMAIL='admin@novustelltravel.com',
)
class TripFeedbackPageTests(TestCase):
    def test_trip_feedback_page_renders(self):
        response = self.client.get(reverse('users:trip-feedback'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Share Your Trip Experience')
        self.assertContains(response, 'Submit Feedback')

    def test_trip_feedback_submission_saves_and_notifies_admin(self):
        response = self.client.post(
            reverse('users:trip-feedback'),
            {
                'trip_name': 'Maasai Mara Safari',
                'destination': 'Maasai Mara',
                'full_name': 'Test Traveler',
                'email': 'traveler@example.com',
                'public_review_permission': 'anonymous',
                'overall_rating': '9',
                'recommend_score': '10',
                'transport_rating': '8',
                'highlights': ['organization', 'guide'],
                'privacy_consent': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(TripFeedback.objects.count(), 1)
        feedback = TripFeedback.objects.get()
        self.assertEqual(feedback.highlights, ['organization', 'guide'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['admin@novustelltravel.com'])
