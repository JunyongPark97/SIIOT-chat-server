import json

from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import ChatRoom, ChatMessage
from chat.serializers import ChatMessageSerializer

from .utils import add_user_as_active_websocket, add_user_as_inactive_websocket
from .exceptions import UserNotLoggedInError


# - NOTE: ALL channel_layer methods are asynchronous
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the user object (provided by the TokenAuthMiddleware in SIIOT_chat_server/routing.py)
        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        if self.user.is_anonymous:
            await self.close()

        self.room_group_name = 'chat_%s' % str(self.room_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await add_user_as_active_websocket(self.user)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await add_user_as_inactive_websocket(self.user)

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):

        if not self.user.is_authenticated:
            raise UserNotLoggedInError()
        print(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive chat_message from room group and send down to client(s)
    async def chat_message(self, message):
        await self._send_consumer_to_client(
            event=message
        )

    # The following is called by the CONSUMER to send the message to the CLIENT
    async def _send_consumer_to_client(self, event):
        await self.send(text_data=json.dumps(event))

