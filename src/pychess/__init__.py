from .controller import Controller


__all__ = ['run']


def run():
    controller = Controller()
    controller.run()
