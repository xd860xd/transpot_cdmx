from .base import *
from .base import BASE_DIR, os

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST=["http://localhost:5500"]


STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

STATICFILES_DIRS = (BASE_DIR, "static")


STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
