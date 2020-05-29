from .errors import LoadError


class ExceptionHandler(object):

    def __init__(self, exceptions, replacement=None):
        self.exceptions = exceptions
        self.replacement = replacement

    def __call__(self, wrapped_func):
        def wrapper(*args, **kwargs):
            try:
                return wrapped_func(*args, **kwargs)
            except self.exceptions:
                return self.replacement
        return wrapper

    @classmethod
    def require_audio(cls):
        return cls(LoadError, None)