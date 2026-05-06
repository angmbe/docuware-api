from decimal import Decimal, InvalidOperation

from django.db import transaction

from documents.models import Document
from documents_items.models import DocumentDetail


DEFAULT_CREATED_BY = 1
DOCUMENT_FIELD_MAX_LENGTHS = {
    "customer": 50,
    "suppliername": 100,
    "notes": 100,
    "currency": 3,
}
DETAIL_FIELD_MAX_LENGTHS = {
    "unit_measure_description": 100,
    "description": 255,
}


def truncate(value, max_length):
    if value is None:
        return None

    return str(value)[:max_length]


def parse_decimal(value, default="0.00"):
    if value in (None, ""):
        value = default

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal(default)


def parse_integer(value, default=0):
    decimal_value = parse_decimal(value, default=default)
    return int(decimal_value)


def get_created_by(value):
    if value in (None, ""):
        return DEFAULT_CREATED_BY

    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("El parametro 'created_by' debe ser numerico.") from exc


def parse_documenttype_id(value):
    if value in (None, ""):
        return None

    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("El campo tipo_comprobante de SUNAT debe ser numerico.") from exc


def build_document_defaults(item, created_by):
    emisor = item.get("emisor") or {}
    cliente = item.get("cliente") or {}
    detalle = item.get("detalle") or {}
    totales = item.get("totales") or {}
    url_descarga = item.get("url_descarga") or {}

    return {
        "customer": truncate(
            cliente.get("numero_documento") or cliente.get("nombre_cliente"),
            DOCUMENT_FIELD_MAX_LENGTHS["customer"],
        ),
        "suppliername": truncate(
            emisor.get("razon_social"),
            DOCUMENT_FIELD_MAX_LENGTHS["suppliername"],
        ),
        "documenttype_id": parse_documenttype_id(detalle.get("tipo_comprobante")),
        "documentdate": detalle.get("fecha_emision"),
        "amount": parse_decimal(totales.get("total_valor_venta")),
        "taxamount": parse_decimal(totales.get("total_igv")),
        "totalamount": parse_decimal(totales.get("monto_total_general")),
        "documenturl": url_descarga.get("pdf") or url_descarga.get("xml"),
        "notes": truncate(detalle.get("estado_comprobante"), DOCUMENT_FIELD_MAX_LENGTHS["notes"]),
        "currency": truncate(detalle.get("codigo_moneda"), DOCUMENT_FIELD_MAX_LENGTHS["currency"]),
        "created_by": created_by,
    }


def build_detail_instances(item, created_by):
    emisor = item.get("emisor") or {}
    detalle = item.get("detalle") or {}
    suppliernumber = emisor.get("ruc") or ""
    documentserial = detalle.get("serie") or ""
    documentnumber = detalle.get("numero") or ""
    detail_instances = []

    for detail_item in item.get("items") or []:
        detail_instances.append(
            DocumentDetail(
                suppliernumber=suppliernumber,
                documentserial=documentserial,
                documentnumber=documentnumber,
                unit_measure_description=truncate(
                    detail_item.get("unidad_medida_descripcion"),
                    DETAIL_FIELD_MAX_LENGTHS["unit_measure_description"],
                ),
                description=truncate(
                    detail_item.get("descripcion"),
                    DETAIL_FIELD_MAX_LENGTHS["description"],
                ),
                quantity=parse_integer(detail_item.get("cantidad")),
                unit_value=parse_decimal(detail_item.get("valor_unitario")),
                tax_value=parse_decimal(detail_item.get("impuesto_valor")),
                total_value=parse_decimal(detail_item.get("valor_venta")),
                created_by=created_by,
            )
        )

    return detail_instances


def import_documentos_sunat(items, created_by=None):
    created_by = get_created_by(created_by)
    documents_created = 0
    documents_updated = 0
    details_created = 0

    with transaction.atomic():
        for item in items:
            emisor = item.get("emisor") or {}
            detalle = item.get("detalle") or {}
            suppliernumber = emisor.get("ruc")
            documentserial = detalle.get("serie")
            documentnumber = detalle.get("numero")

            if not (suppliernumber and documentserial and documentnumber):
                continue

            defaults = build_document_defaults(item, created_by)
            document, created = Document.objects.update_or_create(
                suppliernumber=suppliernumber,
                documentserial=documentserial,
                documentnumber=documentnumber,
                defaults=defaults,
            )

            if created:
                documents_created += 1
            else:
                documents_updated += 1

            DocumentDetail.objects.filter(
                suppliernumber=document.suppliernumber,
                documentserial=document.documentserial,
                documentnumber=document.documentnumber,
            ).delete()

            detail_instances = build_detail_instances(item, created_by)
            DocumentDetail.objects.bulk_create(detail_instances)
            details_created += len(detail_instances)

    return {
        "documents_created": documents_created,
        "documents_updated": documents_updated,
        "details_created": details_created,
    }
