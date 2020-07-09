from django.conf.urls import url, include
from django.urls import path
from rest_framework.routers import SimpleRouter

# from chats.views import ChatRoomViewSet
from chat import views
from chat.views import ChatMessageViewSet

router = SimpleRouter()
router.register('chat', ChatMessageViewSet)


urlpatterns = [
    path('', include(router.urls)),
    url(r'^chat/$', views.index, name='index'),
    url(r'^chat/(?P<room_name>[^/]+)/$', views.room, name='room'),
]
