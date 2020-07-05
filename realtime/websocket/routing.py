from django.conf.urls import url
from . import consumers
from chat import views

websocket_urlpatterns = [
	url(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer)
	# url(r'^ws/chat/$', consumers.ChatConsumer),
	# url(r'^$', views.index, name='index')
	# url(r'^(?P<room_name>[^/]+)/$', views.room, name='room')
]