import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from core.apps.websocket.services.services import get_group_name


class EventsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        self.user = user
        self.station = None
        if hasattr(user, "station") and self.user is not None:
            self.station = self.user.station
        if self.station is None:
            logging.warning("user station not assign")
            await self.close()
            return
        self.group = get_group_name(self.scope.get("host", ""), self.station)
        if user is None or not user.is_authenticated:
            logging.warning("Muvofaqiyatsiz ulanishga urunish")
            await self.close(4001)
            return
        logging.info("Yangi ulanish user=%s group=%s" % (user.pk, self.group))
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        logging.info("Websocket uzulish code=%s user=%s", close_code, self.user.pk if self.user is not None else None)
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message")
        if message is None:
            message = "💀"
        logging.info(
            "Websocket yangi xabar data=%s user=%s", text_data, self.user.pk if self.user is not None else None
        )
        await self.channel_layer.group_send(self.group, {"type": "chat_message", "data": message})

    async def chat_message(self, event):
        message = event.get("data")
        logging.info("send message group=%s" % self.group)
        await self.send(text_data=json.dumps(message))
