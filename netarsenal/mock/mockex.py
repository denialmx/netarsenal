#################################################################################
# Mock Exceptions
#################################################################################
class MockException(Exception):
    """
    Base Mock Exception Class
    """


class InvalidMockDataFile(MockException):
    """
    Exception raised when the mock data file
    is incorrect or corrupted
    """


class MockDeviceNotFound(MockException):
    """
    Exception raised when the mock data file
    does not have the device and or command saved
    """


class MockSimulateFailure(MockException):
    """
    Exception raised when the mock data file
    does not have the device and or command saved
    """
