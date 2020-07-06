# This is just a general exception used by our websocket consumer to direct appropriate error responses to the client


class ChatClientError(Exception):
    """
    Custom exception class that is caught by the websocket receive()
    handler and translated into a send back to the client.
    """

    ERROR_CODE = 0
    ERROR_MESSAGE = "Client error."

    def __init__(self):
        self.type = "ERROR"
        self.error_code = self.ERROR_CODE
        self.error_message = self.ERROR_MESSAGE


class UserNotLoggedInError(ChatClientError):
    ERROR_CODE = 1
    ERROR_MESSAGE = "You are not logged in."

    def __init__(self):
        super().__init__()
