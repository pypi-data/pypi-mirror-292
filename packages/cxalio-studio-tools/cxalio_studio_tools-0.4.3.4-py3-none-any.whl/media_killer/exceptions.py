from cx_core.app import CxException


class NoProfileError(CxException):

    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class NoSourcesError(CxException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class UserCanceledError(CxException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)
