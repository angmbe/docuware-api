import threading
import uuid
from datetime import datetime, timezone

from django.db import close_old_connections

from .services import get_documentos_sunat, get_apisunat_timeout


JOBS = {}
JOBS_LOCK = threading.Lock()
ASYNC_REQUEST_TIMEOUT_SECONDS = 120
ASYNC_TOTAL_TIMEOUT_SECONDS = 900


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def get_async_timeout(setting_name, default_value):
    return get_apisunat_timeout(setting_name, default_value)


def get_job(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        return dict(job) if job else None


def update_job(job_id, **values):
    with JOBS_LOCK:
        if job_id in JOBS:
            JOBS[job_id].update(values)
            return dict(JOBS[job_id])

    return None


def run_documentos_sunat_job(job_id, fecha_inicio, fecha_fin, created_by):
    close_old_connections()
    update_job(job_id, status="running", started_at=utc_now())

    try:
        result = get_documentos_sunat(
            fecha_inicio,
            fecha_fin,
            created_by=created_by,
            request_timeout=get_async_timeout(
                "APISUNAT_ASYNC_TIMEOUT_SECONDS",
                ASYNC_REQUEST_TIMEOUT_SECONDS,
            ),
            total_timeout=get_async_timeout(
                "APISUNAT_ASYNC_TOTAL_TIMEOUT_SECONDS",
                ASYNC_TOTAL_TIMEOUT_SECONDS,
            ),
        )
    except Exception as exc:
        update_job(
            job_id,
            status="error",
            message=str(exc),
            finished_at=utc_now(),
        )
    else:
        update_job(
            job_id,
            status="completed",
            message="Documentos SUNAT obtenidos correctamente",
            result=result,
            finished_at=utc_now(),
        )
    finally:
        close_old_connections()


def start_documentos_sunat_job(fecha_inicio, fecha_fin, created_by=None):
    job_id = uuid.uuid4().hex
    job = {
        "job_id": job_id,
        "status": "pending",
        "message": "Consulta SUNAT en cola",
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "created_by": created_by,
        "created_at": utc_now(),
        "started_at": None,
        "finished_at": None,
        "result": None,
    }

    with JOBS_LOCK:
        JOBS[job_id] = job

    thread = threading.Thread(
        target=run_documentos_sunat_job,
        args=(job_id, fecha_inicio, fecha_fin, created_by),
        daemon=True,
    )
    thread.start()

    return dict(job)
