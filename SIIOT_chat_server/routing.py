from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter

from realtime.websocket.token_auth import TokenAuthMiddlewareStack
from realtime.websocket.routing import websocket_urlpatterns

import realtime

from realtime import consumers

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
            URLRouter(
                realtime.websocket.routing.websocket_urlpatterns
            )
        ),
    # 'websocket': TokenAuthMiddlewareStack(
    #     URLRouter(websocket_urlpatterns)
    # ),
    # 'channel': ChannelNameRouter({
    #     'realtime-event-sender': consumers.EventSenderConsumer,
    # }),
})