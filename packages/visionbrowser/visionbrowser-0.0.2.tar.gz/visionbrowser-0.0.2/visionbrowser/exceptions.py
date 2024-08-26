class APIError(Exception):
    """Custom exception for API errors"""
    pass


class FailedConnection(APIError):
    """An exception was raised when the connection failed to the Vision Browser at your URL."""
    def __init__(self, message: str = "Failed to connect to Vision Browser at your url"):
        self.message = message
        super().__init__(self.message)


class UndefinedPort(APIError):
    """An exception was raised when the port is None"""
    def __init__(self, message: str = "The port was found to be empty after the application/process returned. Most likely the profile was launched inside Vision, or some other issue occurred."):
        self.message = message
        super().__init__(self.message)
