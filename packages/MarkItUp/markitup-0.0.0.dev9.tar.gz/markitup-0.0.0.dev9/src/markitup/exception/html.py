from markitup.exception import MarkItUpException as _MarkItUpException


class MarkItUpHTMLException(_MarkItUpException):
    """Base class for all exceptions raised by `markitup.html` module.

    Attributes
    ----------
    html : str
        The HTML that failed to be parsed.
    """

    def __init__(self, message: str):
        super().__init__(message=message)
        return


class MarkItUpHTMLElementError(MarkItUpHTMLException):
    """Exception raised when an HTML element is invalid.
    """

    def __init__(self, message: str):
        super().__init__(message=f"Invalid HTML element: {message}")
        return
