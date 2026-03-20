from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import PurchaseOrder, PurchaseOrderDetail


class PurchaseOrderCreateViewTests(APITestCase):
    def test_create_purchase_order_with_details(self):
        payload = {
            "orderNo": "OC-0001",
            "supplierID": 10,
            "documentAssociatedType": 2,
            "documentAssociatedNo": "FAC-1001",
            "paymentCondition": 1,
            "currency": 1,
            "guideNo": "GUIA-01",
            "store": 3,
            "purchaseState": 1,
            "createdBy": 99,
            "details": [
                {
                    "descriptionItem": "Item 1",
                    "quantity": 2,
                    "unitPrice": "15.50",
                    "total": "31.00",
                },
                {
                    "descriptionItem": "Item 2",
                    "quantity": 1,
                    "unitPrice": "20.00",
                    "total": "20.00",
                },
            ],
        }

        response = self.client.post(
            reverse("purchase-order-create"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "Orden de compra creada correctamente")
        self.assertEqual(PurchaseOrder.objects.count(), 1)
        self.assertEqual(PurchaseOrderDetail.objects.count(), 2)

        purchase_order = PurchaseOrder.objects.get()
        first_detail = PurchaseOrderDetail.objects.filter(
            purchaseOrderID=purchase_order
        ).order_by("purchaseDetailID").first()

        self.assertEqual(purchase_order.orderNo, "OC-0001")
        self.assertEqual(first_detail.createdBy, 99)
        self.assertEqual(len(response.data["data"]["details"]), 2)

    def test_create_purchase_order_requires_details(self):
        payload = {
            "orderNo": "OC-0002",
            "createdBy": 99,
            "details": [],
        }

        response = self.client.post(
            reverse("purchase-order-create"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("details", response.data["data"])

    def test_get_purchase_order_with_details_by_id(self):
        purchase_order = PurchaseOrder.objects.create(
            orderNo="OC-0100",
            supplierID=5,
            createdBy=10,
        )
        PurchaseOrderDetail.objects.create(
            purchaseOrderID=purchase_order,
            descriptionItem="Servicio 1",
            quantity=3,
            unitPrice="12.50",
            total="37.50",
            createdBy=10,
        )

        response = self.client.get(
            reverse("purchase-order-detail", args=[purchase_order.purchaseOrderID])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["purchaseOrderID"], purchase_order.purchaseOrderID)
        self.assertEqual(len(response.data["data"]["details"]), 1)
        self.assertEqual(response.data["data"]["details"][0]["descriptionItem"], "Servicio 1")

    def test_get_purchase_order_by_id_returns_404_when_not_found(self):
        response = self.client.get(reverse("purchase-order-detail", args=[9999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "Orden de compra no encontrada")

    def test_get_purchase_orders_returns_all_orders(self):
        first_order = PurchaseOrder.objects.create(orderNo="OC-0001", createdBy=1)
        second_order = PurchaseOrder.objects.create(orderNo="OC-0002", createdBy=1)

        PurchaseOrderDetail.objects.create(
            purchaseOrderID=first_order,
            descriptionItem="Item A",
            quantity=1,
            unitPrice="10.00",
            total="10.00",
            createdBy=1,
        )
        PurchaseOrderDetail.objects.create(
            purchaseOrderID=second_order,
            descriptionItem="Item B",
            quantity=2,
            unitPrice="20.00",
            total="40.00",
            createdBy=1,
        )

        response = self.client.get(reverse("purchase-order-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "Ordenes de compra obtenidas correctamente")
        self.assertEqual(len(response.data["data"]), 2)
        self.assertEqual(response.data["data"][0]["purchaseOrderID"], second_order.purchaseOrderID)
        self.assertEqual(len(response.data["data"][0]["details"]), 1)
