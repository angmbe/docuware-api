from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from .importers import build_document_defaults
from .services import ApisunatError, build_rce_headers, get_documentos_sunat, validate_date_range


class ApisunatServiceTests(SimpleTestCase):
    def test_validate_date_range_rejects_different_months(self):
        with self.assertRaisesMessage(ValueError, "Solo se puede buscar dentro del mismo mes."):
            validate_date_range("2026-05-31", "2026-06-01")

    def test_validate_date_range_returns_period(self):
        start_date, end_date, period = validate_date_range("2026-05-02", "2026-05-05")

        self.assertEqual(start_date.isoformat(), "2026-05-02")
        self.assertEqual(end_date.isoformat(), "2026-05-05")
        self.assertEqual(period, "202605")

    @override_settings(APISUNAT_BEARER_TOKEN="test-token")
    def test_build_rce_headers_includes_bearer_token(self):
        headers = build_rce_headers()

        self.assertEqual(headers["Authorization"], "Bearer test-token")

    @override_settings(APISUNAT_BEARER_TOKEN=None)
    def test_build_rce_headers_requires_bearer_token(self):
        with self.assertRaisesMessage(ApisunatError, "No se configuro el token Bearer"):
            build_rce_headers()

    def test_build_document_defaults_uses_tipo_comprobante_as_integer_documenttype_id(self):
        defaults = build_document_defaults(
            {
                "emisor": {"razon_social": "Proveedor"},
                "cliente": {"numero_documento": "20129605490"},
                "detalle": {
                    "tipo_comprobante": "01",
                    "fecha_emision": "2026-05-02",
                    "codigo_moneda": "PEN",
                },
                "totales": {
                    "total_valor_venta": "10.00",
                    "total_igv": "1.80",
                    "monto_total_general": "11.80",
                },
            },
            created_by=1,
        )

        self.assertEqual(defaults["documenttype_id"], 1)

    @patch("apisunat.services.import_documentos_sunat")
    @patch("apisunat.services.fetch_rce_page")
    def test_get_documentos_sunat_fetches_all_pages_and_filters_by_date(
        self,
        fetch_rce_page,
        import_documentos_sunat,
    ):
        import_documentos_sunat.return_value = {
            "documents_created": 2,
            "documents_updated": 0,
            "details_created": 2,
        }
        fetch_rce_page.side_effect = [
            {
                "success": True,
                "payload": {
                    "paginate": {"total_pages": 2, "total_items": 3},
                    "items": [
                        {"detalle": {"fecha_emision": "2026-05-01"}, "id": "outside-start"},
                        {"detalle": {"fecha_emision": "2026-05-02"}, "id": "inside-first"},
                    ],
                },
            },
            {
                "success": True,
                "payload": {
                    "paginate": {"total_pages": 2, "total_items": 3},
                    "items": [
                        {"detalle": {"fecha_emision": "2026-05-05"}, "id": "inside-second"},
                        {"detalle": {"fecha_emision": "2026-05-06"}, "id": "outside-end"},
                    ],
                },
            },
        ]

        result = get_documentos_sunat("2026-05-02", "2026-05-05")

        self.assertEqual(result["period"], "202605")
        self.assertEqual(result["total_pages"], 2)
        self.assertEqual(result["total_items_filtrados"], 2)
        self.assertEqual(result["import_summary"]["documents_created"], 2)
        self.assertEqual([item["id"] for item in result["items"]], ["inside-first", "inside-second"])
        self.assertEqual(fetch_rce_page.call_count, 2)
        import_documentos_sunat.assert_called_once()
