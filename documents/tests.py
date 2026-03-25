from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalogos.models import Catalogo
from proveedores.models import Proveedor

from .models import PurchaseOrder, PurchaseOrderDetail, TipoDocumento


class PurchaseOrderCreateViewTests(APITestCase):
    def setUp(self):
        self.supplier = Proveedor.objects.create(
            supplierno="PRV-001",
            suppliername="Proveedor Test",
        )
        self.document_type = TipoDocumento.objects.create(tipo="Factura")
        self.payment_condition = Catalogo.objects.create(
            tipo_catalogo="CONDICION_PAGO",
            codigo="CONTADO",
            descripcion="Contado",
            estado=True,
        )
        self.currency = Catalogo.objects.create(
            tipo_catalogo="MONEDA",
            codigo="PEN",
            descripcion="Sol",
            estado=True,
        )
        self.store = Catalogo.objects.create(
            tipo_catalogo="ALMACEN",
            codigo="PRINCIPAL",
            descripcion="Almacen principal",
            estado=True,
        )
        self.purchase_state = Catalogo.objects.create(
            tipo_catalogo="ESTADO_OC",
            codigo="APROBADO",
            descripcion="Aprobado",
            estado=True,
        )
        self.purchase_state_rejected = Catalogo.objects.create(
            tipo_catalogo="ESTADO_OC",
            codigo="RECHAZADO",
            descripcion="Rechazado",
            estado=True,
        )

    def test_create_purchase_order_with_details(self):
        payload = {
            "orderNo": "OC-0001",
            "supplierID": self.supplier.supplierid,
            "documentAssociatedType": self.document_type.tipoid,
            "documentAssociatedNo": "FAC-1001",
            "paymentCondition": self.payment_condition.id,
            "currency": self.currency.id,
            "guideNo": "GUIA-01",
            "store": self.store.id,
            "purchaseState": self.purchase_state.id,
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
        self.assertEqual(response.data["data"]["supplierID"]["supplierid"], self.supplier.supplierid)
        self.assertEqual(
            response.data["data"]["documentAssociatedType"]["tipoid"],
            self.document_type.tipoid,
        )

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
            supplierID=self.supplier,
            documentAssociatedType=self.document_type,
            paymentCondition=self.payment_condition,
            currency=self.currency,
            store=self.store,
            purchaseState=self.purchase_state,
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
        self.assertEqual(response.data["data"]["supplierID"]["supplierid"], self.supplier.supplierid)
        self.assertEqual(response.data["data"]["paymentCondition"]["id"], self.payment_condition.id)
        self.assertEqual(response.data["data"]["currency"]["id"], self.currency.id)
        self.assertEqual(response.data["data"]["store"]["id"], self.store.id)
        self.assertEqual(response.data["data"]["purchaseState"]["id"], self.purchase_state.id)
        self.assertEqual(
            response.data["data"]["documentAssociatedType"]["tipoid"],
            self.document_type.tipoid,
        )

    def test_get_purchase_order_by_id_returns_404_when_not_found(self):
        response = self.client.get(reverse("purchase-order-detail", args=[9999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "Orden de compra no encontrada")

    def test_get_purchase_orders_returns_all_orders(self):
        first_order = PurchaseOrder.objects.create(
            orderNo="OC-0001",
            supplierID=self.supplier,
            documentAssociatedType=self.document_type,
            paymentCondition=self.payment_condition,
            currency=self.currency,
            store=self.store,
            purchaseState=self.purchase_state,
            createdBy=1,
        )
        second_order = PurchaseOrder.objects.create(
            orderNo="OC-0002",
            supplierID=self.supplier,
            documentAssociatedType=self.document_type,
            paymentCondition=self.payment_condition,
            currency=self.currency,
            store=self.store,
            purchaseState=self.purchase_state,
            createdBy=1,
        )

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
        self.assertEqual(response.data["data"][0]["supplierID"]["supplierid"], self.supplier.supplierid)
        self.assertEqual(
            response.data["data"][0]["documentAssociatedType"]["tipoid"],
            self.document_type.tipoid,
        )

    def test_post_purchase_order_status_updates_order(self):
        purchase_order = PurchaseOrder.objects.create(
            orderNo="OC-0200",
            purchaseState=self.purchase_state,
            createdBy=10,
        )

        response = self.client.post(
            reverse("purchase-order-status-update"),
            {
                "purchaseOrderID": purchase_order.purchaseOrderID,
                "purchaseState": self.purchase_state_rejected.id,
                "updatedBy": 25,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "La orden ha sido actualizado con exito")
        self.assertEqual(response.data["data"], "La orden ha sido actualizado con exito")

        purchase_order.refresh_from_db()
        self.assertEqual(purchase_order.purchaseState_id, self.purchase_state_rejected.id)
        self.assertEqual(purchase_order.updatedBy, 25)
        self.assertIsNotNone(purchase_order.updatedAt)

    def test_post_purchase_order_status_requires_fields(self):
        response = self.client.post(
            reverse("purchase-order-status-update"),
            {"purchaseOrderID": 1},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("purchaseState", response.data["data"]["required_fields"])
        self.assertIn("updatedBy", response.data["data"]["required_fields"])

    def test_post_purchase_order_status_returns_404_when_not_found(self):
        response = self.client.post(
            reverse("purchase-order-status-update"),
            {
                "purchaseOrderID": 9999,
                "purchaseState": self.purchase_state_rejected.id,
                "updatedBy": 25,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "Orden de compra no encontrada")
