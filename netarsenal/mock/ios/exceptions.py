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
