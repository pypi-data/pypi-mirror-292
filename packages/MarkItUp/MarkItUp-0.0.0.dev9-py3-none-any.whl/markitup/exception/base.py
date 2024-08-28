class MarkItUpException(Exception):
    """Base exception for the markitup package."""

    def __init__(self, message: str):
        super().__init__(message)
        return
