class WlcException(Exception):
    """
    Base Exception Class.
    """

    pass


class CallableFunctionUndefined(WlcException):
    """
    Exception raised when there is no mapping
    between platform and function to be called
    """

    pass


class RequiredParameterMissing(WlcException):
    """
    Exception raised when there is no mapping
    between platform and function to be called
    """

    pass
