class BizError(RuntimeError):
    def __init__(self, code, message):
        super().__init__(code, message)

    @property
    def code(self):
        return self.args[0]

    @property
    def message(self):
        return self.args[1]


class RequestValidationError(BizError):
    def __init__(self):
        super().__init__(400, "Validation Error")


class Forbidden(BizError):
    def __init__(self):
        super().__init__(403, "Forbidden")


class MethodNotAllowed(BizError):
    def __init__(self):
        super().__init__(405, "Method Not Allowed")


class UnsupportedMediaType(BizError):
    def __init__(self):
        super().__init__(415, "Unsupported Media Type")


class InternalServerError(BizError):
    def __init__(self):
        super().__init__(500, "Internal Server Error")
