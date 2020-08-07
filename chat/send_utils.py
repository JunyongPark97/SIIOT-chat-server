from chat.models import ChatRoom
from asgiref.sync import async_to_sync


def send_new_message(channel_layer, room_group_name, message):
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'chat_message',
            'message': message
        }
    )


def send_new_image(channel_layer, room_group_name, image):
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'chat_image',
            'image': image
        }
    )


class MessageSender(object):
    """
    Client에 메세지를 보낼 때 사용하는 함수들을 모아놓은 class입니다.
    """
    def __init__(self, channel_layer, room_id):
        self.channel_layer = channel_layer
        self.room_id = room_id
        self.room_group_name = 'chat_%s' % str(self.room_id)

    @property
    def room(self):
        return ChatRoom.objects.get(id=self.room_id)

    def deliver_message(self, chat_msg):
        send_new_message(self.channel_layer, self.room_group_name, chat_msg)

    def deliver_image(self, chat_img):
        send_new_image(self.channel_layer, self.room_group_name, chat_img)



