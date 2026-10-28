class DeckDispatchError(Exception):
    """Base domain exception for DeckDispatch."""

    def __init__(self, message: str, code: str = "DECK_DISPATCH_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class CompilationError(DeckDispatchError):
    """Raised when compilation of presentation or slide fails."""

    def __init__(self, message: str):
        super().__init__(message, code="COMPILATION_ERROR")


class InvalidColorError(DeckDispatchError):
    """Raised when a color hex string is invalid."""

    def __init__(self, message: str):
        super().__init__(message, code="INVALID_COLOR_ERROR")


class ImageProcessingError(DeckDispatchError):
    """Raised when base64 decoding or image dimensions processing fails."""

    def __init__(self, message: str):
        super().__init__(message, code="IMAGE_PROCESSING_ERROR")


class UnsupportedLayoutError(DeckDispatchError):
    """Raised when an unhandled slide layout is encountered."""

    def __init__(self, message: str):
        super().__init__(message, code="UNSUPPORTED_LAYOUT_ERROR")
