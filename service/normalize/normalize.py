

class InvalidInputDataException(Exception):
    """Exception raised when invalid input data is provided"""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)
