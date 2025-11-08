# type: ignore
import logging
from typing import Any
from config.env import env
from django.core.management import BaseCommand
import redis
from core.apps.api.ocpp.handlers import OcppHandler
from core.apps.api.schemas import Events
from core.apps.api.schemas.events import EventsEnum
from core.apps.customer.models import Domain
from django_tenants.utils import tenant_context


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:
        client = redis.Redis(host=env.str("REDIS_HOST", "redis"))
        logging.info("event handler ishga tushdi")
        self.stdout.write(self.style.SUCCESS("event handler ishga tushdi"))
        try:
            ocpp_handler = OcppHandler()
            while True:
                try:
                    _, message = client.blpop("events")
                    logging.info("new event data=%s", message)
                    event = Events.model_validate_json(message)
                    handlers = {
                        EventsEnum.CHANGE_CONNECTOR_STATUS.value: ocpp_handler.change_connector_status,
                        EventsEnum.START_TRANSACTION.value: ocpp_handler.start_transaction,
                        EventsEnum.STOP_TRANSACTION.value: ocpp_handler.stop_transaction,
                        EventsEnum.METER_VALUE.value: ocpp_handler.meter_value,
                        EventsEnum.HEALTH.value: ocpp_handler.health,
                        EventsEnum.DATA_TRANSFER.value: ocpp_handler.data_transfer,
                        EventsEnum.CONNECT_CHARGER.value: ocpp_handler.connect_charger,
                        EventsEnum.DISCONNECT_CHARGER.value: ocpp_handler.disconnect_charger,
                    }
                    handler = handlers.get(event.event)
                    if handler is None:
                        logging.error("handler not found event=%s", event.event)
                        continue
                    try:
                        tenant = Domain.objects.filter(domain=event.domain)
                    except Domain.DoesNotExist:
                        logging.error("Tenant not found domain=%s", event.domain)
                        return
                    with tenant_context(tenant):
                        handler(event)
                except Exception as e:
                    logging.error("events handler error event=%s", event.event)
                    logging.critical(e)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("event handler to'xtatildi"))
        logging.info("event handler to'xtatildi")
