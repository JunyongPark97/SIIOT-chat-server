WEBSOCKET_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class NewMessageEvent:
    def __init__(self, uuid, chat_uuid, sender_uuid, sender_username, message, date, from_current_user):
        self._type = "chat_message"
        self._uuid = uuid
        self._chat_uuid = chat_uuid
        self._sender_uuid = sender_uuid
        self._sender_username = sender_username
        self._message = message
        self._date = date
        self._from_current_user = from_current_user

    @property
    def type(self):
        return self._type

    @property
    def uuid(self):
        return str(self._uuid)

    @property
    def chat_uuid(self):
        return str(self._chat_uuid)

    @property
    def sender_uuid(self):
        return str(self._sender_uuid)

    @property
    def sender_username(self):
        return self._sender_username

    @property
    def message(self):
        return self._message

    @property
    def date(self):
        return self._date.strftime(WEBSOCKET_DATETIME_FORMAT)

    @property
    def from_current_user(self):
        return str(self._from_current_user)

    @property
    def properties_dict(self):
        return dict(
            type=self.type,
            uuid=self.uuid,
            chat_uuid=self.chat_uuid,
            sender_uuid=self.sender_uuid,
            sender_username=self.sender_username,
            message=self.message,
            date=self.date,
            from_current_user=self.from_current_user,
        )