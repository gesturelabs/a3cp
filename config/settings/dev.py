import sys

from .prod import *  # noqa: F401,F403

# Make local apps importable
sys.path.append(str(BASE_DIR / "apps"))  # noqa: F405

# Local development overrides
SECRET_KEY = "dev-insecure-key"  # any non-empty string is fine for local
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}
