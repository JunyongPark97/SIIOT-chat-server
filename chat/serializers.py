# -*- encoding: utf-8 -*-

from django.conf import settings
from rest_framework import serializers
from chat.models import ChatRoom, ChatMessage

User = settings.AUTH_USER_MODEL


class ChatRoomSerializer(serializers.ModelSerializer):
    seller = serializers.SerializerMethodField()
    buyer = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ('id', 'buyer', 'seller')

    def get_buyer(self, obj):
        buyer = self.context['buyer']
        serializer = ChatUserSerializer(buyer)
        return serializer.data

    def get_seller(self, obj):
        seller = self.context['seller']
        serializer = ChatUserSerializer(seller)
        return serializer.data


class ChatUserSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'nickname', 'profile_image_url')

    def get_nickname(self, obj):
        return obj.nickname

    def get_prodfile_image_url(self, obj):
        return obj.profile.profile_img.url


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    ChatMessage object를 생성할 때 or ChatMessage log를 불러올 때 사용합니다.
    """

    class Meta:
        model = ChatMessage
        fields = (
            'message_type',
            'room',
            'text',
            'message_image'
        )
