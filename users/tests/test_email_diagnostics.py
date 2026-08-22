from django.test import SimpleTestCase

from users.email_diagnostics import build_email_error_details


class FakeResponse:
    status_code = 403

    def json(self):
        return {"message": "domain is not verified"}


class FakeEmailError(Exception):
    status_code = 403
    response = FakeResponse()
    esp_name = "Resend"


class EmailDiagnosticsTests(SimpleTestCase):
    def test_build_email_error_details_keeps_safe_provider_status(self):
        details = build_email_error_details(FakeEmailError("request failed"))

        self.assertEqual(details["code"], "resend-403-FakeEmailError")
        self.assertEqual(details["provider"], "Resend")
        self.assertEqual(details["status_code"], 403)
        self.assertEqual(details["exception"], "FakeEmailError")
        self.assertEqual(details["detail"], "domain is not verified")
