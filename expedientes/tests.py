import shutil
import tempfile
import json
from pathlib import Path

from django.test import override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from documents.models import Document, PurchaseOrder

from .models import ExpedienteDocumento


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


class ExpedienteListCreateViewTests(APITestCase):
    def setUp(self):
        self.temp_media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.temp_media_root)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(lambda: shutil.rmtree(self.temp_media_root, ignore_errors=True))

        self.document = Document.objects.create(
            customer="Cliente 1",
            documentdate="2026-03-26",
            amount="100.00",
            taxamount="18.00",
            totalamount="118.00",
            created_by=1,
        )
        self.purchase_order = PurchaseOrder.objects.create(
            orderNo="OC-0001",
            createdBy=1,
        )

    def test_post_expediente_creates_master_and_detail_records(self):
        payload = {
            "facturaid": self.document.documentid,
            "ordencompraid": self.purchase_order.purchaseOrderID,
            "estado": True,
            "createdby": 7,
            "expediente_documentos": [
                {
                    "tipodocumentoid": 1,
                    "filename": "factura.pdf",
                    "filepath": "expedientes/2026/03/EXP-0001/factura.pdf",
                    "estado": True,
                    "createdby": 7,
                },
                {
                    "tipodocumentoid": 2,
                    "filename": "orden_compra.pdf",
                    "filepath": "expedientes/2026/03/EXP-0001/orden_compra.pdf",
                    "estado": True,
                    "createdby": 7,
                },
            ],
        }

        response = self.client.post(
            reverse("expedientes-list-create"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "Expediente creado correctamente")
        self.assertEqual(response.data["data"]["facturaid"], self.document.documentid)
        self.assertEqual(response.data["data"]["factura"]["documentid"], self.document.documentid)
        self.assertEqual(response.data["data"]["ordencompraid"], self.purchase_order.purchaseOrderID)
        self.assertEqual(
            response.data["data"]["ordencompra"]["purchaseOrderID"],
            self.purchase_order.purchaseOrderID,
        )
        self.assertEqual(len(response.data["data"]["expediente_documentos"]), 2)

    def test_post_expediente_with_pdf_files_creates_records_and_stores_files(self):
        factura_file = SimpleUploadedFile(
            "factura.pdf",
            b"%PDF-1.4 factura pdf",
            content_type="application/pdf",
        )
        orden_file = SimpleUploadedFile(
            "orden_compra.pdf",
            b"%PDF-1.4 orden compra pdf",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("expedientes-list-create"),
            {
                "facturaid": self.document.documentid,
                "ordencompraid": self.purchase_order.purchaseOrderID,
                "createdby": 7,
                "expediente_documentos": json.dumps(
                    [
                        {
                            "tipodocumentoid": 1,
                            "file_field": "factura_file",
                            "createdby": 7,
                        },
                        {
                            "tipodocumentoid": 2,
                            "file_field": "orden_file",
                            "createdby": 7,
                        },
                    ]
                ),
                "factura_file": factura_file,
                "orden_file": orden_file,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]["expediente_documentos"]), 2)

        first_file_path = Path(self.temp_media_root) / response.data["data"]["expediente_documentos"][0]["filepath"]
        second_file_path = Path(self.temp_media_root) / response.data["data"]["expediente_documentos"][1]["filepath"]
        self.assertTrue(first_file_path.exists())
        self.assertTrue(second_file_path.exists())

    def test_get_expedientes_returns_all_records(self):
        create_response = self.client.post(
            reverse("expedientes-list-create"),
            {
                "facturaid": self.document.documentid,
                "ordencompraid": self.purchase_order.purchaseOrderID,
                "createdby": 1,
                "expediente_documentos": [
                    {
                        "tipodocumentoid": 1,
                        "filename": "factura.pdf",
                        "filepath": "expedientes/2026/03/EXP-0001/factura.pdf",
                    }
                ],
            },
            format="json",
        )
        self.client.post(
            reverse("expedientes-list-create"),
            {
                "facturaid": self.document.documentid,
                "createdby": 2,
            },
            format="json",
        )

        response = self.client.get(reverse("expedientes-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 2)
        self.assertEqual(response.data["data"][0]["expedienteid"], create_response.data["data"]["expedienteid"] + 1)
        self.assertEqual(response.data["data"][1]["factura"]["documentid"], self.document.documentid)
        self.assertEqual(
            response.data["data"][1]["ordencompra"]["purchaseOrderID"],
            self.purchase_order.purchaseOrderID,
        )

    def test_get_expedientes_filters_by_expedienteid(self):
        first_response = self.client.post(
            reverse("expedientes-list-create"),
            {
                "facturaid": self.document.documentid,
                "createdby": 1,
            },
            format="json",
        )
        self.client.post(
            reverse("expedientes-list-create"),
            {
                "ordencompraid": self.purchase_order.purchaseOrderID,
                "createdby": 2,
            },
            format="json",
        )

        response = self.client.get(
            reverse("expedientes-list-create"),
            {"expedienteid": first_response.data["data"]["expedienteid"]},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(
            response.data["data"][0]["expedienteid"],
            first_response.data["data"]["expedienteid"],
        )
        self.assertEqual(response.data["data"][0]["factura"]["documentid"], self.document.documentid)

    def test_post_expediente_documento_upload_creates_file_and_record(self):
        expediente_response = self.client.post(
            reverse("expedientes-list-create"),
            {
                "facturaid": self.document.documentid,
                "createdby": 1,
            },
            format="json",
        )
        expedienteid = expediente_response.data["data"]["expedienteid"]
        pdf_file = SimpleUploadedFile(
            "sustento.pdf",
            b"%PDF-1.4 expediente document",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("expedientes-documentos-upload", args=[expedienteid]),
            {
                "tipodocumentoid": 5,
                "createdby": 7,
                "file": pdf_file,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(
            response.data["message"],
            "Documento del expediente cargado correctamente",
        )
        self.assertEqual(ExpedienteDocumento.objects.count(), 1)
        self.assertEqual(response.data["data"]["tipodocumentoid"], 5)

        expected_file_path = Path(self.temp_media_root) / response.data["data"]["filepath"]
        self.assertTrue(expected_file_path.exists())

    def test_post_expediente_documento_upload_returns_404_when_expediente_not_found(self):
        pdf_file = SimpleUploadedFile(
            "sustento.pdf",
            b"%PDF-1.4 expediente document",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("expedientes-documentos-upload", args=[9999]),
            {
                "tipodocumentoid": 5,
                "file": pdf_file,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "Expediente no encontrado")

    def test_post_expediente_documento_upload_requires_pdf_file(self):
        expediente_response = self.client.post(
            reverse("expedientes-list-create"),
            {
                "facturaid": self.document.documentid,
                "createdby": 1,
            },
            format="json",
        )
        expedienteid = expediente_response.data["data"]["expedienteid"]
        txt_file = SimpleUploadedFile(
            "sustento.txt",
            b"plain text",
            content_type="text/plain",
        )

        response = self.client.post(
            reverse("expedientes-documentos-upload", args=[expedienteid]),
            {
                "tipodocumentoid": 5,
                "file": txt_file,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("file", response.data["data"])
