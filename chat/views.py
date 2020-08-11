from django.utils.safestring import mark_safe
import json, uuid

from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from accounts.models import User
from products.models import Product
from chat.models import ChatRoom, ChatMessage, ChatMessageImages
from chat.send_utils import MessageSender
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.pagination import SiiotPagination
from django.db.models import Q, F
from datetime import datetime

from .serializers import ChatMessageReadSerializer, ChatMessageWriteSerializer, ChatRoomSerializer
from realtime.websocket.utils import _set_user_websocket_activity, add_user_as_active_websocket,\
    add_user_as_inactive_websocket, check_if_websocket_is_active

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


class ChatRoomViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    queryset = ChatRoom.objects.filter(Q(buyer_active=True) | Q(seller_active=True))
    permission_classes = [IsAuthenticated, ]
    serializer_class = ChatRoomSerializer

    def create(self, request, *args, **kwargs):
        """
        상품 detail page에서 문의하기 버튼을 눌렀을 때 ChatRoom object 생성하면서 chatroom id return
        api : POST api/v1/chatroom/
        data: {'seller_id': seller_id, 'buyer_id': buyer_id, 'product_id': product_id}
        :return: id (Int)
        """
        data = request.data
        seller_id = data.get('seller_id', None)
        buyer_id = data.get('buyer_id', None)
        product_id = data.get('product_id', None)
        seller = get_object_or_404(User, pk=seller_id)
        buyer = get_object_or_404(User, pk=buyer_id)
        product = get_object_or_404(Product, pk=product_id)
        chatroom, _ = ChatRoom.objects.get_or_create(seller=seller, buyer=buyer, product=product)
        return Response({'room_id': chatroom.id}, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """
        해당 user가 속해있는 chatroom list info를 모두 뿌려줍니다.
        api : GET api/v1/chatroom/
        """
        # 해당 유저가 속해있는 방 최신 message created_at 순서로 만든 후에 serializer 형태로 제공
        qs = self.get_queryset()
        user = request.user
        chatroom_qs = qs.filter(Q(buyer=user) | Q(seller=user)).exclude(created_at=F("updated_at"))\
            .order_by('updated_at')
        serializer = self.get_serializer(chatroom_qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def exit(self, request, pk):
        """
        user가 속해있는 chatroom 참여자에서 제외시켜주는 API 입니다.
        만약 seller, buyer 모두 chatroom에 존재하지 않는다면 chatroom의 active를 변경합니다.
        api : PUT chatroom/{room_id}/exit
        """
        user = request.user
        chat_room = get_object_or_404(ChatRoom, pk=pk)
        if chat_room.buyer != user and chat_room.seller != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            if chat_room.buyer == user:
                chat_room.buyer_active = False
                chat_room.save()
            elif chat_room.seller == user:
                chat_room.seller_active = False
                chat_room.save()
            qs = self.get_queryset()
            chatroom_qs = qs.filter(Q(buyer=user) | Q(seller=user)).order_by('updated_at')
            serializer = self.get_serializer(chatroom_qs, many=True)

            return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)


class ChatMessageViewSet(viewsets.GenericViewSet):
    queryset = ChatRoom.objects.filter(Q(buyer_active=True) | Q(seller_active=True))
    permission_classes = [IsAuthenticated, ]

    def get_serializer_class(self):
        if self.action == 'deliver':
            return ChatMessageReadSerializer
        elif self.action == 'message':
            return ChatMessageWriteSerializer
        else:
            return super(ChatMessageViewSet, self).get_serializer_class()

    @action(methods=['get'], detail=True)
    def deliver(self, request, pk):
        """
        message를 room 및 user 등에게 deliver합니다.
        api: GET chat/{room_id}/deliver
        """
        user = request.user
        chat_room = get_object_or_404(ChatRoom, pk=pk)
        if chat_room.buyer != user and chat_room.seller != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            message_qs = chat_room.messages.all().order_by('-created_at')
            unread_qs = message_qs.exclude(owner=user)
            for unread_msg in unread_qs:
                unread_msg.is_read = True
                unread_msg.save()
            # sender = _get_sender(room_id=chat_room.id)
            # for message in message_qs:
            #     sender.deliver_message(chat_msg=message.text)
            paginator = SiiotPagination()
            page = paginator.paginate_queryset(message_qs, request)
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

    @action(methods=['post'], detail=True)
    def message(self, request, pk):
        """
        message object 생성 & chat room 에 message를 channel을 통해 보내는 API 입니다.
        api: POST chat/{room_id}/message
        data: {'message_type' : Int, 'text' : String, 'image_key' : [String]}
        """
        user = request.user
        data = request.data
        message_type = request.data.get('message_type')
        if message_type == 1:
            image_key_list = []
            text = request.data.get('text', None)
            if text is None:
                Response(status=status.HTTP_404_NOT_FOUND)
        else:
            text = None
            image_key_list = request.data.get('image_key', None)
            if not image_key_list or not isinstance(image_key_list, list):
                Response(status=status.HTTP_400_BAD_REQUEST)
        chat_room = get_object_or_404(ChatRoom, pk=pk)
        if not chat_room.buyer:
            chat_room.buyer_active = True
            chat_room.save()
        if not chat_room.seller:
            chat_room.seller_active = True
            chat_room.save()
        if chat_room.buyer != user and chat_room.seller != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            data.update(owner=user.id)
            data.update(room=chat_room.id)
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            new_message = serializer.save()
            chat_room.updated_at = datetime.now()
            chat_room.save()
            # new_message = ChatMessage(room=chat_room, text=text, owner=user)
            # new_message.save()
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
                sender.deliver_message(chat_msg=new_message.text, owner=user.id)
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

