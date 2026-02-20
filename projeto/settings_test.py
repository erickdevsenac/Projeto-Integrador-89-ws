from pathlib import Path

from .settings import *  # noqa: F403

BASE_DIR = Path(__file__).resolve().parent.parent


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}
