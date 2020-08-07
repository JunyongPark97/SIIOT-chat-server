# -*- encoding: utf-8 -*-

from django.conf import settings
from rest_framework import serializers
from chat.models import ChatRoom, ChatMessage

User = settings.AUTH_USER_MODEL


class ChatUserSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'nickname', 'profile_image_url']

    def get_nickname(self, obj):
        return obj.nickname

    def get_profile_image_url(self, obj):
        return obj.profile.profile_img.url


class ChatRoomSerializer(serializers.ModelSerializer):
    seller = serializers.SerializerMethodField()
    buyer = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ('id', 'product', 'deal', 'updated_at', 'buyer', 'seller', 'unread_count')

    def get_product(self, obj):
        result = {
            'id': obj.product.id,
            'name': obj.product.name,
            'price': obj.product.price,
            'image_url': obj.product.prodthumbnail.thumbnail.url
        }
        return result

    def get_buyer(self, obj):
        result = {
            'id': obj.buyer.id,
            'nickname': obj.buyer.nickname,
            'profile_image_url': obj.buyer.profile.profile_image_url
        }
        return result

    def get_seller(self, obj):
        result = {
            'id': obj.seller.id,
            'nickname': obj.seller.nickname,
            'profile_image_url': obj.seller.profile.profile_image_url
        }
        return result

    def get_unread_count(self, obj):
        count = 0
        unread_qs = obj.messages.filter(is_read=False)
        for unread in unread_qs:
            count = count + 1
        return count


class ChatMessageReadSerializer(serializers.ModelSerializer):
    """
    쌓여진 ChatMessage 를 방에 deliver 할 때 or ChatMessage log를 참고하는 serializer 입니다.
    """
    message_image_url = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ('message_type', 'text', 'created_at', 'message_image_url', 'owner')

    def get_message_image_url(self, obj):
        try:
            return obj.images.image_url
        except:
            return None


class ChatMessageWriteSerializer(serializers.ModelSerializer):
    """
    ChatMessage 를 write 할 때 사용하는 serializer 입니다.
    """

    class Meta:
        model = ChatMessage
        fields = ('room', 'message_type', 'text', 'created_at', 'owner')


