class BaseException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class OkExit(BaseException):
    def __init__(self, message="Your settings have been saved to model configuration"):
        super().__init__(message)


class KoExit(BaseException):
    def __init__(self, message="Exit and clear all field configuration!"):
        super().__init__(message)


class DoneExit(BaseException):
    def __init__(self, message="Your database model has been setup successful!"):
        super().__init__(message)


class HintExit(BaseException):
    def __init__(self, message):
        super().__init__(message)


class UnCommitError(BaseException): ...


class BreakAndExit(BaseException): ...


class CancelExit(BaseException): ...


class InvalidAttr(BaseException): ...


class ModelNotFoud(BaseException): ...
