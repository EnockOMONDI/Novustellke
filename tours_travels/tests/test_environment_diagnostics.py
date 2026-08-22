from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from tours_travels.environment_diagnostics import environment_diagnostics


class StaffUser:
    is_active = True
    is_staff = True
    is_authenticated = True
    pk = 1

    def has_module_perms(self, app_label):
        return False

    def has_perm(self, permission):
        return False

    def get_username(self):
        return "environment-admin"


class EnvironmentDiagnosticsTests(SimpleTestCase):
    def setUp(self):
        self.url = reverse("environment_diagnostics")
        self.request_factory = RequestFactory()

    def test_anonymous_user_is_redirected_to_admin_login(self):
        request = self.request_factory.get(self.url)
        request.user = AnonymousUser()

        response = environment_diagnostics(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            f"{reverse('admin:login')}?next={self.url}",
        )

    @patch.dict(
        "os.environ",
        {
            "DJANGO_SETTINGS_MODULE": "tours_travels.settings_prod",
            "SECRET_KEY": "must-not-appear",
            "DATABASE_URL": "postgresql://must-not-appear",
            "RESEND_API_KEY": "re_must-not-appear",
        },
        clear=True,
    )
    def test_staff_page_shows_presence_without_values(self):
        request = self.request_factory.get(self.url)
        request.user = StaffUser()

        response = environment_diagnostics(request)
        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Environment diagnostics", content)
        self.assertIn("RESEND_API_KEY", content)
        self.assertIn("Present", content)
        self.assertNotIn("must-not-appear", content)
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")

    def test_non_staff_user_is_redirected(self):
        request = self.request_factory.get(self.url)
        request.user = StaffUser()
        request.user.is_staff = False

        response = environment_diagnostics(request)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("admin:login")))
