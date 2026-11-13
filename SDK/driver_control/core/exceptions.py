class ServoControlError(Exception):
    """Base exception for driver_control."""


class AnalyzerClosedError(ServoControlError):
    """Raised when an operation is attempted on a closed Analyzer."""


class AnalyzerTimeoutError(ServoControlError):
    """Raised when an Analyzer response does not arrive before the timeout."""


class ProtocolError(ServoControlError):
    """Raised for malformed frames or unsupported protocol state."""


class CRCError(ProtocolError):
    """Raised when a response CRC check fails."""
