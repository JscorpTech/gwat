from datetime import timedelta
import logging
from unittest.mock import patch
from django.utils import timezone
import pytest
from core.apps.api.enums.connectors import ConnectorStatusEnum
from core.apps.api.models.transaction import TransactionModel
from core.apps.api.tasks.charger import check_fail_chargers


@pytest.fixture
def instance(db):
    instance = TransactionModel._baker()
    instance.conn.status = ConnectorStatusEnum.CHARGING.value
    instance.conn.save()
    instance.conn.charger.last_health = timezone.now() - timedelta(minutes=10)
    instance.conn.charger.save()
    return instance


def test_check_fail_chargers(instance: TransactionModel):
    with patch("core.apps.api.tasks.charger.ws_connector_event") as mock_event, patch(
        "core.apps.api.tasks.charger.stop_transaction"
    ) as mock_stop_transaction:
        logging.info(instance)
        check_fail_chargers()
        mock_stop_transaction.assert_called()
        mock_event.assert_called()
