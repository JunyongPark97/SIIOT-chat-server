from django.shortcuts import render
from django.utils.safestring import mark_safe
import json

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.serializers import Serializer
from chat.models import ChatRoom
from chat.send_utils import MessageSender

from channels import layers


def index(request):
    return render(request, 'chat/index.html', {})


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })


def _get_sender(room_id):
    channel_layer = layers.get_channel_layer()
    return MessageSender(channel_layer=channel_layer,
                         room_id=room_id)


class ChatMessageViewSet(viewsets.GenericViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = Serializer

    @action(methods=['post'], detail=True)
    def deliver(self, request, pk=None):
        """
        message를 room 및 user 등에게 deliver합니다.
        """
        chat_room = self.get_object()
        message_qs = chat_room.messages.all()
        sender = _get_sender(room_id=chat_room.id)
        for message in message_qs:
            sender.deliver_message(chat_msg=message.text)
        return Response()


