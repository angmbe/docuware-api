from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalogos.models import Catalogo

from .models import Proveedor


class ProveedorListCreateViewTests(APITestCase):
    def setUp(self):
        self.bank_bcp = Catalogo.objects.create(
            tipo_catalogo="BANCO",
            codigo="BCP",
            descripcion="Banco de Credito",
            estado=True,
        )
        self.bank_bbva = Catalogo.objects.create(
            tipo_catalogo="BANCO",
            codigo="BBVA",
            descripcion="Banco BBVA",
            estado=True,
        )

    def test_get_proveedores_returns_all_records_with_bank_relations(self):
        Proveedor.objects.create(
            supplierno="PRV-001",
            suppliername="Proveedor Uno",
            bank1=self.bank_bcp,
            bank2=self.bank_bbva,
        )
        Proveedor.objects.create(
            supplierno="PRV-002",
            suppliername="Proveedor Dos",
        )

        response = self.client.get(reverse("proveedores-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 2)
        self.assertEqual(response.data["data"][0]["bank1"]["codigo"], "BCP")
        self.assertEqual(response.data["data"][0]["bank2"]["codigo"], "BBVA")

    def test_get_proveedores_filters_by_supplierno(self):
        Proveedor.objects.create(
            supplierno="PRV-001",
            suppliername="Proveedor Uno",
        )
        Proveedor.objects.create(
            supplierno="PRV-002",
            suppliername="Proveedor Dos",
        )

        response = self.client.get(
            reverse("proveedores-list-create"),
            {"supplierno": "prv-002"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["supplierno"], "PRV-002")

    def test_post_proveedor_creates_record(self):
        payload = {
            "supplierno": "PRV-003",
            "suppliername": "Proveedor Tres",
            "address": "Av. Principal 123",
            "phone": "999999999",
            "email": "proveedor3@test.com",
            "bank1_id": self.bank_bcp.id,
            "accountno1": "001-123456789",
            "bank2_id": self.bank_bbva.id,
            "accountno2": "002-987654321",
            "createdby": 7,
            "updatedby": 7,
        }

        response = self.client.post(
            reverse("proveedores-list-create"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "Proveedor creado correctamente")
        self.assertEqual(Proveedor.objects.count(), 1)

        proveedor = Proveedor.objects.select_related("bank1", "bank2").get()
        self.assertEqual(proveedor.suppliername, "Proveedor Tres")
        self.assertEqual(proveedor.bank1_id, self.bank_bcp.id)
        self.assertEqual(proveedor.bank2_id, self.bank_bbva.id)
        self.assertEqual(response.data["data"]["bank1"]["codigo"], "BCP")
        self.assertEqual(response.data["data"]["bank2"]["codigo"], "BBVA")

    def test_post_proveedor_requires_suppliername(self):
        response = self.client.post(
            reverse("proveedores-list-create"),
            {"supplierno": "PRV-004"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("suppliername", response.data["data"])
