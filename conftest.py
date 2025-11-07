# type: ignore
"""
Global pytest configuration for all django-tenants tests.

This conftest.py is at the project root and provides tenant fixtures
for all test modules across the entire project.
"""
import pytest
from django.db import connection


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    """Customize database settings for tenant tests."""
    pass


@pytest.fixture(scope="session", autouse=True)
def setup_test_tenants(django_db_setup, django_db_blocker):
    """
    Automatically create test tenants once per test session.

    This runs once at the start of the test session and creates:
    - Public tenant (schema: 'public')
    - Test tenant (schema: 'test')

    All tests will use the 'test' tenant.
    """
    from core.apps.customer.models import Client, Domain

    with django_db_blocker.unblock():
        # Create public tenant
        public_tenant, _ = Client.objects.get_or_create(
            schema_name="public", defaults={"name": "Public Tenant", "paid_until": "2099-12-31", "on_trial": False}
        )
        Domain.objects.get_or_create(domain="localhost", tenant=public_tenant, defaults={"is_primary": True})

        # Create test tenant
        test_tenant, _ = Client.objects.get_or_create(
            schema_name="test", defaults={"name": "Test Tenant", "paid_until": "2099-12-31", "on_trial": False}
        )
        Domain.objects.get_or_create(domain="test.localhost", tenant=test_tenant, defaults={"is_primary": True})


@pytest.fixture
def tenant(db):
    """
    Provide test tenant for tests.

    Usage:
        def test_something(tenant):
            # tenant is already set in connection
            assert tenant.schema_name == 'test'
    """
    from core.apps.customer.models import Client

    tenant = Client.objects.get(schema_name="test")
    connection.set_tenant(tenant)
    return tenant


@pytest.fixture
def tenant_context_fixture(tenant):
    """
    Switch to tenant context for tests.

    Usage:
        @pytest.mark.django_db
        def test_something(tenant_context_fixture):
            # Code runs in tenant schema
            pass
    """
    connection.set_tenant(tenant)
    yield tenant


@pytest.fixture
def api_client(tenant):
    """
    API client configured for tenant requests.

    Usage:
        def test_api(api_client):
            response = api_client.get('/api/endpoint/')
            assert response.status_code == 200
    """
    from rest_framework.test import APIClient
    from django_tenants.test.client import TenantClient

    client = TenantClient(tenant)
    api_client = APIClient()
    api_client.tenant = tenant

    connection.set_tenant(tenant)

    original_request = api_client.request

    def tenant_request(**kwargs):
        connection.set_tenant(tenant)
        if "HTTP_HOST" not in kwargs:
            kwargs["HTTP_HOST"] = "test.localhost"
        return original_request(**kwargs)

    api_client.request = tenant_request
    return api_client
