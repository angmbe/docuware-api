import json
import time
from datetime import date
from socket import timeout as SocketTimeout
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings

from .importers import import_documentos_sunat


APISUNAT_RCE_URL = "https://dev.apisunat.pe/api/v1/sunat/rce"
APISUNAT_TIMEOUT_SECONDS = 10
APISUNAT_TOTAL_TIMEOUT_SECONDS = 20


class ApisunatError(Exception):
    pass


def parse_iso_date(value, field_name):
    if not value:
        raise ValueError(f"El parametro '{field_name}' es obligatorio.")

    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            f"El parametro '{field_name}' debe tener formato YYYY-MM-DD."
        ) from exc


def validate_date_range(fecha_inicio, fecha_fin):
    start_date = parse_iso_date(fecha_inicio, "fecha_inicio")
    end_date = parse_iso_date(fecha_fin, "fecha_fin")

    if start_date > end_date:
        raise ValueError("La fecha_inicio no puede ser mayor que fecha_fin.")

    if start_date.year != end_date.year or start_date.month != end_date.month:
        raise ValueError("Solo se puede buscar dentro del mismo mes.")

    return start_date, end_date, start_date.strftime("%Y%m")


def build_rce_url(period, page):
    query = urlencode({"period": period, "page": page})
    return f"{APISUNAT_RCE_URL}?{query}"


def build_rce_headers():
    token = getattr(settings, "APISUNAT_BEARER_TOKEN", None)
    if not token:
        raise ApisunatError("No se configuro el token Bearer de Apisunat.")

    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "BackEndDocuware/1.0",
    }


def get_apisunat_timeout(default_name, default_value):
    value = getattr(settings, default_name, default_value)

    try:
        return float(value)
    except (TypeError, ValueError):
        return default_value


def fetch_rce_page(period, page, timeout=None):
    request = Request(
        build_rce_url(period, page),
        headers=build_rce_headers(),
    )
    request_timeout = timeout or get_apisunat_timeout(
        "APISUNAT_TIMEOUT_SECONDS",
        APISUNAT_TIMEOUT_SECONDS,
    )

    try:
        with urlopen(request, timeout=request_timeout) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as exc:
        raise ApisunatError(f"Apisunat respondio con estado HTTP {exc.code}.") from exc
    except URLError as exc:
        raise ApisunatError(f"No se pudo conectar con Apisunat: {exc.reason}.") from exc
    except (TimeoutError, SocketTimeout) as exc:
        raise ApisunatError("La consulta a Apisunat excedio el tiempo de espera.") from exc

    try:
        return json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise ApisunatError("Apisunat retorno una respuesta JSON invalida.") from exc


def parse_item_emission_date(item):
    fecha_emision = item.get("detalle", {}).get("fecha_emision")
    if not fecha_emision:
        return None

    try:
        return date.fromisoformat(fecha_emision)
    except ValueError:
        return None


def filter_items_by_date_range(items, start_date, end_date):
    filtered_items = []

    for item in items:
        emission_date = parse_item_emission_date(item)
        if emission_date and start_date <= emission_date <= end_date:
            filtered_items.append(item)

    return filtered_items


def get_documentos_sunat(fecha_inicio, fecha_fin, created_by=None):
    start_date, end_date, period = validate_date_range(fecha_inicio, fecha_fin)
    started_at = time.monotonic()
    total_timeout = get_apisunat_timeout(
        "APISUNAT_TOTAL_TIMEOUT_SECONDS",
        APISUNAT_TOTAL_TIMEOUT_SECONDS,
    )

    def get_remaining_timeout():
        remaining = total_timeout - (time.monotonic() - started_at)
        if remaining <= 0:
            raise ApisunatError("La consulta a Apisunat excedio el tiempo maximo permitido.")

        return min(
            get_apisunat_timeout("APISUNAT_TIMEOUT_SECONDS", APISUNAT_TIMEOUT_SECONDS),
            remaining,
        )

    first_response = fetch_rce_page(period=period, page=1, timeout=get_remaining_timeout())
    if not first_response.get("success"):
        raise ApisunatError(first_response.get("message") or "Apisunat retorno error.")

    payload = first_response.get("payload") or {}
    paginate = payload.get("paginate") or {}
    total_pages = int(paginate.get("total_pages") or 1)

    filtered_items = filter_items_by_date_range(
        payload.get("items") or [],
        start_date,
        end_date,
    )

    for page in range(2, total_pages + 1):
        page_response = fetch_rce_page(
            period=period,
            page=page,
            timeout=get_remaining_timeout(),
        )
        if not page_response.get("success"):
            raise ApisunatError(
                page_response.get("message") or f"Apisunat retorno error en pagina {page}."
            )

        page_payload = page_response.get("payload") or {}
        filtered_items.extend(
            filter_items_by_date_range(
                page_payload.get("items") or [],
                start_date,
                end_date,
            )
        )

    import_summary = import_documentos_sunat(filtered_items, created_by=created_by)

    return {
        "period": period,
        "fecha_inicio": start_date.isoformat(),
        "fecha_fin": end_date.isoformat(),
        "total_pages": total_pages,
        "total_items_api": paginate.get("total_items"),
        "total_items_filtrados": len(filtered_items),
        "import_summary": import_summary,
        "items": filtered_items,
    }
