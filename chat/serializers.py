# -*- encoding: utf-8 -*-

import re

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from rest_framework import serializers

User = get_user_model()

from chat.models import ChatRoom, ChatMessage


class ChatRoomSerializer(serializers.ModelSerializer):
    seller = serializers.HiddenField(default=serializers.CurrentUserDefault())
    buyer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    websocket_url = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ('id', 'buyer', 'seller', 'websocket_url')

    def get_websocket_url(self, instance):
        domain = Site.objects.get(name='chat').domain
        return 'ws://{domain}/chat/{pk}/'.format(domain=domain, pk=instance.id)


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

