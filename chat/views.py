from django.shortcuts import render
from django.utils.safestring import mark_safe
import json, uuid

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.serializers import Serializer
from rest_framework import status
from chat.models import ChatRoom, ChatMessage, ChatMessageImages
from chat.send_utils import MessageSender
from rest_framework.permissions import IsAuthenticated, AllowAny

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
    permission_classes = [AllowAny, ]

    @action(methods=['get'], detail=True)
    def deliver(self, request, pk=None):
        """
        message를 room 및 user 등에게 deliver합니다.
        api: GET chat/room_id/deliver
        """
        chat_room = self.get_object()
        message_qs = chat_room.messages.all()
        sender = _get_sender(room_id=chat_room.id)
        for message in message_qs:
            sender.deliver_message(chat_msg=message.text)
        return Response()

    @action(methods=['post'], detail=True)
    def message(self, request, *args, **kwargs):
        """
        message object 생성 & chat room 에 message를 channel을 통해 보내는 API 입니다.
        api: POST chat/room_id/message
        data: {'message_type' : Int, 'text' : String, 'image_key' : [String]}
        """
        message_type = self.request.data.get('message_type')
        if message_type == 1:
            image_key_list = []
            text = self.request.data.get('text', None)
            if text is None:
                Response(status=status.HTTP_404_NOT_FOUND)
        else:
            text = None
            image_key_list = self.request.data.get('image_key', None)
            if not image_key_list:
                Response(status=status.HTTP_404_NOT_FOUND)
        chat_room = self.get_object()
        new_message = ChatMessage(room=chat_room, text=text)
        new_message.save()
        # image save
        if not image_key_list or not isinstance(image_key_list, list):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        image_url_list = []
        # image object create
        for key in image_key_list:
            ChatMessageImages.objects.create(message=new_message, image_key=key)
            image_url_list.append(ChatMessageImages.objects.get(message=new_message, image_key=key))

        sender = _get_sender(room_id=chat_room.id)
        if message_type == 1:
            sender.deliver_message(chat_msg=new_message.text)
        else:
            for i in range(len(image_url_list)):
                sender.deliver_image(image_url=image_url_list[i])
        return Response(status=status.HTTP_201_CREATED)


class S3ImageUploadViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]

    @action(methods=['post'], detail=False)
    def image_key_list(self, request):
        """
        이미지 첨부시 uuid list를 발급받는 api 입니다. (TODO : presigned url)
        api: POST api/v1/s3/image_key_list/
        data : {'count' : int}

        """
        data = request.data
        count = int(data['count'])
        temp_key_list = []
        for i in range(count):
            temp_key = self.fun_temp_key()
            temp_key_list.append(temp_key)
        return Response(temp_key_list)

    def fun_temp_key(self):
        ext = 'jpg'
        key = uuid.uuid4()
        image_key = "%s.%s" % (key, ext)
        url = "https://{}.s3.amazonaws.com/".format('siiot-media-storage') # TODO: production s3
        content_type = "image/jpeg"
        data = {"url": url, "image_key": image_key, "content_type": content_type, "key": key}
        return data

