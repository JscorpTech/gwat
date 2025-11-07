import pytest
from django.urls import reverse


@pytest.fixture
def settings_urls():
    return {
        "languages": reverse("settings-languages"),
    }


def test_languages(api_client, settings_urls, tenant_context_fixture):
    response = api_client.get(settings_urls["languages"])
    assert response.status_code == 200
