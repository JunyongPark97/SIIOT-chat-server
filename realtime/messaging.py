# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
#
# from .events import NewMessageEvent
#
#
# channel_layer = get_channel_layer()
#
#
# def send_new_message(message, other_user, from_current_user):
#     _send_realtime_event_to_user(
#         user=other_user,
#         realtime_event=NewMessageEvent(
#             uuid=message.uuid,
#             chat_uuid=message.chat.uuid,
#             sender_uuid=message.user.uuid,
#             sender_username=message.user.username,
#             date=message.created,
#             message=message.text,
#             from_current_user=from_current_user,
#         )
#     )
#
#
# def _send_realtime_event_to_user(user, realtime_event):
#     async_to_sync(channel_layer.send)(
#         "realtime-event-sender",
#         {
#             'type': 'send_event',
#             'user_uuid_str': str(user.uuid),
#             'realtime_event_dict': realtime_event.properties_dict,
#         }
#     )