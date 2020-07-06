# from channels.consumer import AsyncConsumer
# from channels.db import database_sync_to_async
#
# from .websocket.utils import check_if_websocket_is_active
# from django.conf import settings
# from common.exceptions import NotFound
#
#
# # Used when we have to send a realtime event from inside sync code and we don't want it to block (like in a Django View)
# class EventSenderConsumer(AsyncConsumer):
#
#     async def send_event(self, message):
#         try:
#             user = await database_sync_to_async(settings.AUTH_USER_MODEL)
#         except NotFound:
#             return
#
#         if check_if_websocket_is_active(user):
#             print("Realtime: event_sender_consumer_send_event - websocket branch")
#             await send_event_via_websocket_group_consumer(
#                 channel_layer=self.channel_layer,
#                 user=user,
#                 realtime_event_dict=message['realtime_event_dict']
#             )
#         else:
#             raise ConnectionRefusedError
