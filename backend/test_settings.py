from .settings import *  # noqa: F403,F401


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",  # noqa: F405
    }
}

MIGRATION_MODULES = {
    "documents": None,
    "documents_items": None,
    "centro_costo": None,
    "programacion": None,
    "users": None,
    "catalogos": None,
}
