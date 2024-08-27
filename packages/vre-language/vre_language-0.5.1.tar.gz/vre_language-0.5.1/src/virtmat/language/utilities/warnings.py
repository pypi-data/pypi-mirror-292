"""handling domain-specific warnings"""
import warnings


class TextSUserWarning(UserWarning):
    """warning to use within the processors"""


def format_warning_wrapper(func):
    """format domain-specific warnings; leave python warnings unchanged"""
    def wrapper(*args, **kwargs):
        warning = args[0]
        warning_cls = args[1]
        if isinstance(warning, TextSUserWarning):
            assert warning_cls is TextSUserWarning
            return 'Warning: ' + str(warning) + '\n'
        return func(*args, **kwargs)
    return wrapper


warnings.formatwarning = format_warning_wrapper(warnings.formatwarning)
