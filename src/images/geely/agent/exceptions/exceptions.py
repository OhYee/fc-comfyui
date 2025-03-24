class CustomError(Exception):
    """自定义异常基类"""
    def __init__(self, code=500, message=""):
        self.code = code
        self.message = message
        super().__init__(self.message)


class StateTransitionError(CustomError):
    def __init__(self, from_state, to_state):
        msg = f"Illegal state transition: {from_state} -> {to_state}"
        super().__init__(message=msg, code=409)
