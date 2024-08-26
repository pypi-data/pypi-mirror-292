class MidasClientError(Exception):
    """Exception to indicate a general API error."""


class MidasCommunicationError(MidasClientError):
    """Exception to indicate a communication error."""


class MidasAuthenticationError(MidasClientError):
    """Exception to indicate an authentication error."""
