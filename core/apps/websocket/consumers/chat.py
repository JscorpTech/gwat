import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer


class EventsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        self.user = user
        if user is None or not user.is_authenticated:
            logging.warning("Muvofaqiyatsiz ulanishga urunish")
            await self.close(4001)
            return
        logging.info("Yangi ulanish user=%s", user.pk)
        await self.channel_layer.group_add("charger_events", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        logging.info("Websocket uzulish code=%s user=%s", close_code, self.user.pk if self.user is not None else None)
        await self.channel_layer.group_discard("charger_events", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message")
        if message is None:
            message = "💀"
        logging.info(
            "Websocket yangi xabar data=%s user=%s", text_data, self.user.pk if self.user is not None else None
        )
        await self.channel_layer.group_send("charger_events", {"type": "chat_message", "data": message})

    async def chat_message(self, event):
        message = event.get("data")
        await self.send(text_data=json.dumps(message))
