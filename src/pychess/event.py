class Signal:
    def __init__(self, arg_type=None):
        self._arg_type = arg_type or type(None)
        self._connected_callback = None

    def connect(self, callback):
        self._connected_callback = callback

    def emit(self, arg=None):
        if not isinstance(arg, self._arg_type):
            error_msg = (
                f'{self} cannot emit value of type {type(arg)}'
            )
            raise TypeError(error_msg)

        if self._connected_callback is not None:
            if arg is not None:
                self._connected_callback(arg)
            else:
                self._connected_callback()

    def __repr__(self):
        return f'{self.__class__.__name__}'
