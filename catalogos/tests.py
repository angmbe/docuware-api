from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Catalogo


class CatalogoListViewTests(APITestCase):
    def test_get_catalogos_requires_tipo_catalogo(self):
        response = self.client.get(reverse("catalogos-list"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(
            response.data["message"],
            "El parámetro 'tipo_catalogo' es obligatorio",
        )

    def test_get_catalogos_filters_by_tipo_catalogo(self):
        Catalogo.objects.create(
            tipo_catalogo="MONEDA",
            codigo="PEN",
            descripcion="Sol",
            estado=True,
        )
        Catalogo.objects.create(
            tipo_catalogo="MONEDA",
            codigo="USD",
            descripcion="Dólar",
            estado=True,
        )
        Catalogo.objects.create(
            tipo_catalogo="DOCUMENTO",
            codigo="FAC",
            descripcion="Factura",
            estado=True,
        )

        response = self.client.get(
            reverse("catalogos-list"),
            {"tipo_catalogo": "MONEDA"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "Catálogo obtenido correctamente")
        self.assertEqual(len(response.data["data"]), 2)
        self.assertEqual(response.data["data"][0]["codigo"], "PEN")
        self.assertEqual(response.data["data"][1]["codigo"], "USD")

    def test_get_catalogos_accepts_tipo_catalogo_case_insensitive(self):
        Catalogo.objects.create(
            tipo_catalogo="MONEDA",
            codigo="PEN",
            descripcion="Sol",
            estado=True,
        )
        Catalogo.objects.create(
            tipo_catalogo="DOCUMENTO",
            codigo="FAC",
            descripcion="Factura",
            estado=True,
        )

        response = self.client.get(
            reverse("catalogos-list"),
            {"tipo_catalogo": "moneda"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["tipo_catalogo"], "MONEDA")
