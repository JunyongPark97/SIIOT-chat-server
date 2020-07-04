# -*- encoding: utf-8 -*-

import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

from chat.models import ChatRoom, ChatMessage


class ChatRoomSerializer(serializers.ModelSerializer):
    seller = serializers.HiddenField(default=serializers.CurrentUserDefault())
    buyer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    websocket_url = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ('id', 'buyer', 'seller')


class ChatUserSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField()
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'nickname', 'profile_image_url')

    def get_prodfile_image_url(self, obj):
        return obj.profile.profile_img.url


class ChatMessageReadSerializer(serializers.ModelSerializer):
    message_type = serializers.CharField()
    room_id = serializers.IntegerField()
    text = serializers.CharField()
    # source_type = serializers.IntegerField()
    # template = serializers.JSONField()
    # is_hidden = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    class Meta:
        model = ChatMessage
        fields = (
            'id',
            'message_type',
            'room_id',
            'text',
            # 'source_type',
            # 'template',
            # 'is_hidden',
            'created_at',
            'updated_at',
        )


class ChatMessageWriteSerializer(serializers.ModelSerializer):
    """
    ChatMessage object를 생성할 때 사용합니다. (ex: ChatMessageTmpl.save)
    """
    text = serializers.CharField(allow_blank=True, required=False)
    # code = serializers.CharField(allow_blank=True, required=False)
    message_image = serializers.CharField(allow_null=True, required=False)
    # source_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
    #                                                  allow_null=True, required=False)
    # template = serializers.JSONField(allow_null=True, required=False)
    # target_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
    #                                                  allow_null=True, required=False)
    # is_hidden = serializers.BooleanField(default=False)

    class Meta:
        model = ChatMessage
        fields = (
            'message_type',
            'room',
            'text',
            'message_image',
            # 'source_type',
            # 'template',
            # 'target_user',
            # 'is_hidden',
        )


class MessageSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    user_uuid = serializers.ReadOnlyField(source='user.uuid')
    chat_uuid = serializers.ReadOnlyField(source='chat.uuid')
    from_current_user = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = ChatMessage
        fields = ('uuid', 'chat_uuid', 'user_username', 'user_uuid', 'created', 'text', 'from_current_user')

    def get_from_current_user(self, message):
        if 'request' in self.context:
            return self.context['request'].user == message.user
        return None


class ChatSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ('uuid', 'messages',)

    def get_messages(self, chat):
        qs = ChatMessage.objects.filter(chat=chat).order_by('-created')[0:10]
        serializer = MessageSerializer(instance=qs, many=True, context=self.context)
        return serializer.data
