# type: ignore
"""
All urls configurations tree
"""

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from config.env import env


def home(request):
    return HttpResponse("OK: #7b69b18935eed79b437275a84729de719f965e50")


urlpatterns = [
    path("health/", home),
    path("", include("core.apps.accounts.urls")),
    path("api/", include("core.apps.shared.urls")),
    path("api/", include("core.apps.api.urls")),
]
urlpatterns += [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("ckeditor5/", include("django_ckeditor_5.urls"), name="ck_editor_5_upload_file"),
]
if env.bool("SILK_ENABLED", False):
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
if env.str("PROJECT_ENV") == "debug":
    urlpatterns += [
        path("schema/", SpectacularAPIView.as_view(), name="schema"),
        path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
urlpatterns += [
    re_path("static/(?P<path>.*)", serve, {"document_root": settings.STATIC_ROOT}),
    re_path("media/(?P<path>.*)", serve, {"document_root": settings.MEDIA_ROOT}),
]
