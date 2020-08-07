from django.contrib import admin
from chat.models import ChatRoom, ChatMessage, ChatMessageImages
from custom_manage.sites import staff_panel


class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['pk','seller', 'buyer', 'seller_active', 'buyer_active', 'deal', 'product', 'created_at']


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['message_type', 'room', 'text', 'created_at', 'is_read',
                    'owner', 'seller_visible', 'buyer_visible']


class ChatMessageImageAdmin(admin.ModelAdmin):
    list_display = ['message', 'image_key']


staff_panel.register(ChatRoom, ChatRoomAdmin)
staff_panel.register(ChatMessage, ChatMessageAdmin)
staff_panel.register(ChatMessageImages, ChatMessageImageAdmin)
