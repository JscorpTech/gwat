import pytest
from django.urls import reverse

from core.apps.api.models import ChargerModel


@pytest.fixture
def instance(db, tenant_context_fixture):
    return ChargerModel._baker()


@pytest.fixture
def authenticated_user(db, tenant_context_fixture):
    """Create an authenticated superuser for API tests"""
    from core.apps.accounts.models import User
    user = User.objects.create_superuser(
        phone='+998901234567',
        password='testpass123',
        is_staff=True,
        is_superuser=True
    )
    return user


@pytest.fixture
def charger_api_client(instance, api_client, authenticated_user):
    # Authenticate the client
    api_client.force_authenticate(user=authenticated_user)
    return api_client, instance


@pytest.fixture
def data(charger_api_client):
    client, instance = charger_api_client
    return (
        {
            "list": reverse("charger-list"),
            "retrieve": reverse("charger-detail", kwargs={"pk": instance.pk}),
            "retrieve-not-found": reverse("charger-detail", kwargs={"pk": 1000}),
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


# @pytest.mark.django_db
# def test_create(data):
#    urls, client, _ = data
#    response = client.post(urls["list"], data={"name": "test"})
#    assert response.json()["status"] is True
#    assert response.status_code == 201


# @pytest.mark.django_db
# def test_update(data):
#    urls, client, _ = data
#    response = client.patch(urls["retrieve"], data={"name": "updated"})
#    assert response.json()["status"] is True
#    assert response.status_code == 200
#
#    # verify updated value
#    response = client.get(urls["retrieve"])
#    assert response.json()["status"] is True
#    assert response.status_code == 200
#    assert response.json()["data"]["name"] == "updated"


# @pytest.mark.django_db
# def test_partial_update():
#    urls, client, _ = data
#    response = client.patch(urls["retrieve"], data={"name": "updated"})
#    assert response.json()["status"] is True
#    assert response.status_code == 200
#
#    # verify updated value
#    response = client.get(urls["retrieve"])
#    assert response.json()["status"] is True
#    assert response.status_code == 200
#    assert response.json()["data"]["name"] == "updated"


# @pytest.mark.django_db
# def test_destroy(data):
#    urls, client, _ = data
#    response = client.delete(urls["retrieve"])
#    assert response.status_code == 204
