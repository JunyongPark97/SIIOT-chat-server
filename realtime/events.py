
#
# class NewMessageEvent:
#     def __init__(self, message):
#         self._type = "chat_message"
#         self._message = message
#
#     @property
#     def type(self):
#         return self._type
#
#     @property
#     def message(self):
#         return self._message
#
#     @property
#     def properties_dict(self):
#         return dict(
#             type=self.type,
#             message=self.message
#         )