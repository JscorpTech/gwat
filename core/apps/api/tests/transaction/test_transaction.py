import logging
from os import path
import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APIClient

from core.apps.api.models import TransactionModel


@pytest.fixture
def instance(db):
    return TransactionModel._baker()


@pytest.fixture
def api_client(instance):
    client = APIClient()
    client.force_authenticate(user=instance.user)
    return client, instance


@pytest.fixture(autouse=True)
def mock_data():
    with patch("core.apps.api.views.transaction.remote_start_transaction") as mock_start_transaction, patch(
        "core.apps.api.views.transaction.ws_transaction_event"
    ) as mock_events, patch("core.apps.api.views.transaction.remote_stop_transaction") as mock_stop_transaction:
        mock_start_transaction.return_value = True, "salom"
        mock_stop_transaction.return_value = True, "salom"
        yield


@pytest.fixture
def data(api_client):
    client, instance = api_client
    return (
        {
            "list": reverse("transaction-list"),
            "retrieve": reverse("transaction-detail", kwargs={"pk": instance.pk}),
            "retrieve-not-found": reverse("transaction-detail", kwargs={"pk": 1000}),
            "start": reverse("transaction-start"),
            "stop": reverse("transaction-stop"),
            "clear": reverse("transaction-clear"),
        },
        client,
        instance,
    )


@pytest.mark.django_db
def test_list(data):
    urls, client, _ = data
    response = client.get(urls["list"])
    data_resp = response.json()
    assert response.status_code == 200
    assert data_resp["status"] is True


@pytest.mark.django_db
def test_retrieve(data):
    urls, client, _ = data
    response = client.get(urls["retrieve"])
    data_resp = response.json()
    assert response.status_code == 200
    assert data_resp["status"] is True


@pytest.mark.django_db
def test_retrieve_not_found(data):
    urls, client, _ = data
    response = client.get(urls["retrieve-not-found"])
    data_resp = response.json()
    assert response.status_code == 404
    assert data_resp["status"] is False


@pytest.mark.django_db
def test_start_transaction(data):
    urls, client, instance = data
    response = client.post(urls["start"], data={"conn": instance.conn.pk})
    data_resp = response.json()
    assert response.status_code == 200
    assert data_resp["status"] is True
    assert data_resp["data"]["status"] is True
    assert "detail" in data_resp["data"]
    assert data_resp["data"]["detail"] == "salom"


@pytest.mark.django_db
def test_stop_transaction(data):
    urls, client, instance = data
    response = client.post(urls["stop"], data={"transaction": instance.pk})
    data_resp = response.json()
    assert response.status_code == 200
    assert data_resp["status"] is True
    assert data_resp["data"]["status"] is True
    assert "detail" in data_resp["data"]
    assert data_resp["data"]["detail"] == "salom"


@pytest.mark.django_db
def test_clear_transaction(data):
    urls, client, instance = data
    response = client.post(urls["clear"], data={"transaction": instance.pk})
    assert response.json()["status"] is True
