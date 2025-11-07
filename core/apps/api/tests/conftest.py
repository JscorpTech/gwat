"""
Pytest configuration for django-tenants tests.
"""

import pytest
from django.db import connection


@pytest.fixture(scope="session", autouse=True)
def setup_test_tenants(django_db_setup, django_db_blocker):
    """Automatically create test tenants once per test session."""
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
    """Provide test tenant for tests."""
    from core.apps.customer.models import Client

    tenant = Client.objects.get(schema_name="test")
    connection.set_tenant(tenant)
    return tenant


@pytest.fixture
def tenant_context_fixture(tenant):
    """Switch to tenant context for tests."""
    connection.set_tenant(tenant)
    yield tenant


@pytest.fixture
def api_client(tenant):
    """API client configured for tenant."""
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
