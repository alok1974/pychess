import contextlib


from PySide2 import QtWidgets, QtCore, QtGui


__all__ = [QtWidgets, QtCore, QtGui, 'block_signals']


@contextlib.contextmanager
def block_signals(widgets):
    signal_states = []
    for widget in widgets:
        signal_states.append(
            (widget, widget.signalsBlocked())
        )
    try:
        yield
    finally:
        for widget, is_signal_blocked in signal_states:
            widget.blockSignals(is_signal_blocked)
