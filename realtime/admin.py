from django.contrib import admin
from .websocket.models import UserWebSocketActivity


class UserWebSocketActivityAdmin(admin.ModelAdmin):
    model = UserWebSocketActivity
    list_display = ['user', 'active']


admin.site.register(UserWebSocketActivity, UserWebSocketActivityAdmin)
