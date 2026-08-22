from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from tours_travels.context_processors import _missing_manifest_paths, default_images


class DefaultImagesContextProcessorTests(SimpleTestCase):
    def tearDown(self):
        _missing_manifest_paths.clear()

    @override_settings(
        STATIC_URL="/static/",
        DEFAULT_IMAGES={
            "DEFAULT": "assets/images/logo/defaultimagenovustell.png",
            "PLACEHOLDER_SVG": "images/novustelltravelplaceholder.svg",
        },
    )
    @patch(
        "tours_travels.context_processors.static",
        side_effect=ValueError("missing manifest entry"),
    )
    def test_missing_manifest_entry_uses_unhashed_static_url(self, static_mock):
        context = default_images(request=None)

        self.assertEqual(
            context["default_images"].DEFAULT,
            "/static/assets/images/logo/defaultimagenovustell.png",
        )
        self.assertEqual(
            context["default_images"].PLACEHOLDER_SVG,
            "/static/images/novustelltravelplaceholder.svg",
        )
        self.assertEqual(static_mock.call_count, 2)
