from chat.models import ChatRoom


class MessageSender(object):
    """
    Client에 메세지를 보낼 때 사용하는 함수들을 모아놓은 class입니다.
    """
    def __init__(self, channel_layer, room_id, session_data=None):
        self.channel_layer = channel_layer
        self.room_id = room_id
        if not session_data:
            session_data = {}
        self.session_data = session_data
        self.room_group_name = 'chat_%s' % str(self.room_id)

    @property
    def room(self):
        return ChatRoom.objects.get(id=self.room_id)

    async def deliver_message(self, chat_msg, immediately=False):

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': chat_msg
            }
        )
