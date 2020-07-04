from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe

from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import ChatRoom, ChatMessage
from chat.serializers import MessageSerializer

import json

from common.exceptions import MissingRequiredField


def index(request):
    return render(request, 'chat/index.html', {})


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })


class ChatDetails(APIView):

    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated, )
    lookup_field = 'uuid'

    def get_queryset(self):
        queryset = ChatMessage.objects.filter(chat=self.get_object())
        before_date = self.request.query_params.get('created_before', None)

        if before_date is not None:
            queryset = queryset.filter(created__lte=before_date)
        return queryset

    def get_object(self):
        chat_uuid = self.kwargs['uuid']
        obj = get_object_or_404(ChatRoom.objects.all(), uuid=chat_uuid)

        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True, context={'request':request})
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        text = self.request.data.get('text', None)
        if text is None:
            raise MissingRequiredField(missing_field="text")

        new_message = ChatMessage(chat=self.get_object(), user=self.request.user, text=text)
        new_message.save()

        # pass context so that MessageSerializer has access to the current request and user
        serializer = self.serializer_class(new_message, context={'request':request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


