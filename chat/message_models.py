from collections import Mapping
from uuid import UUID

from chat.models import ChatMessage
from chat.serializers import ChatMessageWriteSerializer


#
# Base classes
#
class Serializable(Mapping):
    """
    클래스를 통째로 Serializer에 data 인자로 전달할 수 있도록, dict-like interface를 구현합니다.
    - ex :
        tmpl = MessageTmpl(...)
        serializer = ChatMessageWriteSerializer(data=tmpl)  # tmpl is valid (dict-like object)
    이 클래스를 상속받는 경우, Meta.fields 를 구현하여야 합니다.
    """

    class Meta:
        fields = ()

    # impl for Mapping
    def __getitem__(self, key):
        if not hasattr(self, key):
            raise KeyError(key)
        initial_attr = getattr(self, key)
        if isinstance(initial_attr, Serializable):
            attr = dict(initial_attr)
        elif isinstance(initial_attr, list):
            attr = list(map(lambda x: dict(x) if isinstance(x, Serializable) else x))
        else:
            attr = initial_attr
        return attr

    def __iter__(self):
        for field in self._get_valid_fields():
            yield field

    def __len__(self):
        return len(self._get_valid_fields())

    # show only valid fields
    def _get_valid_fields(self):
        return [field for field in self.Meta.fields if hasattr(self, field)]


class MessageTmplBase(Serializable):
    """
    Base class for Message template.
    MessageTmpl 객체는 ChatMessageSerializer에 전달하여 object로 저장하거나,
    또는 on-the-fly 로 JSON-serialized message를 생성할 수 있습니다.
    """

    class Meta:
        fields = ChatMessageWriteSerializer.Meta.fields

    def __init__(self, source,
                 action_code='chat'):
        """
        :param action_code: 현재 만들고 있는 메세지(=self) 의 action_code
        """
        self.source = source
        self._handler_name = None
        self.action_code = action_code
        self.created_at = None

    #
    # getters
    #

    @property
    def source_type(self):
        return self.source.source_type

    def with_created_at(self, created_at):
        """
        ChatMessage 객체 없이, Tmpl->JSON 으로 serialize할 때 사용.
        """
        self.created_at = created_at
        return self

    def with_room_id(self, room_id):
        """
        write-only. (FIXME: docstring & arg name is ugly)
        """
        self.room = room_id
        return self

    def with_target_user_id(self, target_user_id):
        """
        write-only. (FIXME: docstring & arg name is ugly)
        """
        self.target_user = target_user_id
        return self

    def save(self):
        """
        ChatMessage에 저장합니다.
        :return: ChatMessage object
        :raises: serializers.ValidationError
        """
        serializer = ChatMessageWriteSerializer(data=self)
        serializer.is_valid(raise_exception=True)
        instance = serializer.create(serializer.validated_data)
        return instance

    def update(self, chat_msg):
        """
        ChatMessage 객체에 tmpl을 적용합니다.
        :param chat_msg: ChatMessage object
        :return: ChatMessage object
        :raises: serializers.ValidationError
        """
        serializer = ChatMessageWriteSerializer(chat_msg, data=self)
        serializer.is_valid(raise_exception=True)
        instance = serializer.update(chat_msg, serializer.validated_data)
        return instance


class TextMessageMixin(object):
    @property
    def message_type(self):
        return 1

    def to_text(self):
        return self.text


class ImageMessageMixin(object):
    image_key = None

    @property
    def message_type(self):
        return 2

    def to_text(self):
        return '(사진)'


class TextChatMessageTmpl(MessageTmplBase, TextMessageMixin):
    def __init__(self, source, text, action_code=None):
        super(TextChatMessageTmpl, self).__init__(source)
        self.text = text
        if action_code:
            self.action_code = action_code


class ImageChatMessageTmpl(MessageTmplBase, ImageMessageMixin):
    def __init__(self, source,
                 image_key=None,
                 content_url=None,
                 caption=''):
        super(ImageChatMessageTmpl, self).__init__(source)
        assert image_key or content_url, 'ImageChatMessageTmpl error. image_key and content_url are both None'
        if image_key:
            if isinstance(image_key, UUID):
                image_key = str(image_key)
            self.image_key = image_key


class ButtonsMessageTmpl(MessageTmplBase):
    def __init__(self, source, action_code, actions, text='', thumbnail_image_url=None):
        super(ButtonsMessageTmpl, self).__init__(source=source, action_code=action_code)
        self.text = text
        self.actions = actions
        self.thumbnail_image_url = thumbnail_image_url

    @property
    def message_type(self):
        return 3

    @property
    def template(self):
        return {
            'type': 'buttons',
            'text': self.text,
            'thumbnail_image_url': self.thumbnail_image_url,
            'actions': [action.to_serializable() for action in self.actions]
        }

