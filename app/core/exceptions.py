class DeckBridgeError(Exception):
    """Base domain exception for DeckBridge."""

    def __init__(self, message: str, code: str = "DECK_BRIDGE_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


# Backward-compatible alias
DeckDispatchError = DeckBridgeError


class CompilationError(DeckBridgeError):
    """Raised when compilation of presentation or slide fails."""

    def __init__(self, message: str):
        super().__init__(message, code="COMPILATION_ERROR")


class InvalidColorError(DeckBridgeError):
    """Raised when a color hex string is invalid."""

    def __init__(self, message: str):
        super().__init__(message, code="INVALID_COLOR_ERROR")


class ImageProcessingError(DeckBridgeError):
    """Raised when base64 decoding or image dimensions processing fails."""

    def __init__(self, message: str):
        super().__init__(message, code="IMAGE_PROCESSING_ERROR")


class UnsupportedLayoutError(DeckBridgeError):
    """Raised when an unhandled slide layout is encountered."""

    def __init__(self, message: str):
        super().__init__(message, code="UNSUPPORTED_LAYOUT_ERROR")
