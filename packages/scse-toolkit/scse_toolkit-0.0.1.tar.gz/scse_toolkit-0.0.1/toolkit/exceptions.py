class BaseException(Exception):
    default_message: str | None = None

    def __init__(self, *args: object) -> None:
        try:
            (message, *extra_args) = args
        except ValueError:
            message = None

            if self.default_message is not None:
                return super().__init__(self.default_message, *args)
            else:
                return super().__init__(*args)

        super().__init__(message, *extra_args)


class ApiError(BaseException):
    pass


class InvalidToken(BaseException):
    default_message = "The supplied token is invalid."


class InvalidCredentials(BaseException):
    default_message = "Authentication credentials rejected."


class Forbidden(BaseException):
    default_message = "Authentication credentials indicate insufficient permissions."
