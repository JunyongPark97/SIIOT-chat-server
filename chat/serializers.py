# -*- encoding: utf-8 -*-

import re

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from rest_framework import serializers

User = get_user_model()

from chat.models import ChatRoom, ChatMessage


class ChatRoomSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    websocket_url = serializers.SerializerMethodField()
    another_selves = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ('id', 'room_type', 'owner', 'websocket_url', 'another_selves')

    def get_websocket_url(self, instance):
        domain = Site.objects.get(name='chat').domain
        return 'ws://{domain}/chat/{pk}/'.format(domain=domain, pk=instance.id)

    def validate_room_type(self, value):
        valid_values = ('question', 'answer', 'contact')
        if value not in valid_values:
            raise serializers.ValidationError('invalid room type')
        return value

    def get_another_selves(self, instance):
        return []


class ChatUserSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='social_default_nickname')
    profile_image_url = serializers.CharField(source='social_default_profile_image_url')
    role = serializers.SerializerMethodField()
    is_staff = serializers.BooleanField()

    class Meta:
        model = User
        fields = ('id', 'nickname', 'profile_image_url', 'role', 'is_staff')

    def get_role(self, user):
        role_dict = self.context.get('role_dict', None)
        if not role_dict:
            return 'none'
        return role_dict.get(user.id, 'none')


class ChatMessageReadSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_message_type_display')
    code = serializers.CharField()
    source_type = serializers.IntegerField()
    template = serializers.JSONField()
    text = serializers.CharField()
    is_hidden = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    class Meta:
        model = ChatMessage
        fields = (
            'id',
            'message_type',
            'room_id',
            'text',
            'source_type',
            'template',
            'is_hidden',
            'created_at',
            'updated_at',
        )


class ChatMessageWriteSerializer(serializers.ModelSerializer):
    """
    ChatMessage object를 생성할 때 사용합니다. (ex: ChatMessageTmpl.save)
    """
    text = serializers.CharField(allow_blank=True, required=False)
    code = serializers.CharField(allow_blank=True, required=False)
    image_key = serializers.ImageField(allow_null=True, required=False)

    source_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                                     allow_null=True, required=False)
    template = serializers.JSONField(allow_null=True, required=False)

    target_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                                     allow_null=True, required=False)
    is_hidden = serializers.BooleanField(default=False)

    class Meta:
        model = ChatMessage
        fields = (
            'message_type',
            'room',
            'text',
            'image_key',

            'source_type',

            'template',

            'target_user',
            'is_hidden',
        )

