import shutil
import tempfile
from pathlib import Path

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile


class ExpedienteUploadViewTests(APITestCase):
    def setUp(self):
        self.temp_media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.temp_media_root)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(lambda: shutil.rmtree(self.temp_media_root, ignore_errors=True))

    def test_post_upload_pdf_creates_expected_folder_structure(self):
        pdf_file = SimpleUploadedFile(
            "archivo.pdf",
            b"%PDF-1.4 test pdf content",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("expedientes-upload"),
            {
                "expedienteid": "EXP-0001",
                "file": pdf_file,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

        current_date = Path(response.data["data"]["relative_path"])
        expected_relative_path = Path("expedientes") / current_date.parts[1] / current_date.parts[2] / "EXP-0001" / "archivo.pdf"
        expected_file_path = Path(self.temp_media_root) / expected_relative_path

        self.assertEqual(response.data["data"]["relative_path"], expected_relative_path.as_posix())
        self.assertTrue(expected_file_path.exists())

    def test_post_upload_requires_pdf_file(self):
        txt_file = SimpleUploadedFile(
            "archivo.txt",
            b"plain text",
            content_type="text/plain",
        )

        response = self.client.post(
            reverse("expedientes-upload"),
            {
                "expedienteid": "EXP-0001",
                "file": txt_file,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("file", response.data["data"])

    def test_post_upload_requires_valid_expedienteid(self):
        pdf_file = SimpleUploadedFile(
            "archivo.pdf",
            b"%PDF-1.4 test pdf content",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("expedientes-upload"),
            {
                "expedienteid": "EXP/0001",
                "file": pdf_file,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("expedienteid", response.data["data"])
