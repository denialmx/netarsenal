class ArsenalException(Exception):
    """
    Base Exception Class.
    """

    pass


class CallableFunctionUndefined(ArsenalException):
    """
    Exception raised when there is no mapping
    between platform and function to be called
    """

    pass


class ConfigFileNotFound(ArsenalException):
    """
    Exception raised when there is no mapping
    between platform and function to be called
    """

    pass
