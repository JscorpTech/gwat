TENANT_MODEL = "customer.Client"

TENANT_DOMAIN_MODEL = "customer.Domain"
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)


SHARED_APPS = (
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    #
    "django_tenants",
    "core.apps.customer",
    #
    "channels",
    "django_ckeditor_5",
    "drf_spectacular",
    "rest_framework",
    "corsheaders",
    "django_filters",
    "django_redis",
    "rest_framework_simplejwt",
)
TENANT_APPS = [
    "core.apps.accounts",
    "cacheops",
    "core.apps.websocket",
    "modeltranslation",
    "core.apps.api",
    "django_core",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.apps.shared",
]


TENANT_ADMIN_SCHEMA = "admin"
