class Signal:
    def __init__(self, arg_type=None):
        self._arg_type = arg_type or type(None)
        self._connected_callbacks = []

    def connect(self, callback):
        self._validate_callback(callback)
        self._connected_callbacks.append(callback)

    def emit(self, arg=None):
        if not isinstance(arg, self._arg_type):
            error_msg = (
                f'{self} cannot emit value of type {type(arg)}'
            )
            raise TypeError(error_msg)

        for callback in self._connected_callbacks:
            if callback is not None:
                if arg is not None:
                    callback(arg)
                else:
                    callback()

    def disconnect(self, callback):
        self._validate_callback(callback)
        if callback in self._connected_callbacks:
            self._connected_callbacks.remove(callback)

    def _validate_callback(self, callback):
        if not callable(callback):
            error_msg = f'Callback {callback} is not a callable!'
            raise TypeError(error_msg)

    def __repr__(self):
        return f'{self.__class__.__name__}'
