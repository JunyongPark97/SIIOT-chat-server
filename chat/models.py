from django.db import models
from django.conf import settings

from payment.models import Deal

import jsonfield


def img_directory_path_message(instance, filename):
    return 'chatroom/{}/message/{}'.format(instance.room.id, filename)


class ChatRoom(models.Model):
    room_type = models.CharField(max_length=30, db_index=True, help_text='채팅방 유형')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='seller_chat_rooms',
                               on_delete=models.SET_NULL)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='buyer_chat_rooms',
                              on_delete=models.SET_NULL)
    active = models.BooleanField(default=True, help_text='웹소켓 채팅이 가능할 경우 True')
    deal = models.OneToOneField(Deal, help_text='채팅방에 연관된 deal id', null=True,
                                related_name='chat_room', on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    # normal fields
    MESSAGE_TYPES = (
        # 추후 업데이트는 SIIOT BOT이 CARD 형태로 전달하기 떄문에 message_type을 늘리거나 action_code 작성 필요
        (1, 'text'),
        (2, 'image')
        # (3, 'templates'),
        # (4, 'postback'),
    )
    message_type = models.IntegerField(choices=MESSAGE_TYPES, db_index=True)
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    text = models.TextField()
    message_image = models.ImageField(null=True, blank=True, upload_to=img_directory_path_message)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(default=False)

    # source(=author) fields
    # 추후 업데이트는 SIIOT BOT이 CARD 형태로 전달하기 때문에 source_type 봇 추가 필요
    # SOURCE_TYPES = (
    #     (1, 'user'),
    #     (2, 'bot')
    # )
    # source_type = models.IntegerField(choices=SOURCE_TYPES, db_index=True)

    # template data fields
    # template = jsonfield.JSONField(default=dict)

    # target fields
    # target_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='targeted_chat_messages',
    #                                 blank=True, null=True, on_delete=models.SET_NULL)
    # is_hidden = models.BooleanField(default=True)


