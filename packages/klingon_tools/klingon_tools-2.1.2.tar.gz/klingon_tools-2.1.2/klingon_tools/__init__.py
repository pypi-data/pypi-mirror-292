from .logtools import LogTools as _LogTools


class LogTools(_LogTools):

    def __init__(self, debug=False):
        super().__init__(debug)


__version__ = "0.0.0"

__all__ = ["LogTools"]
