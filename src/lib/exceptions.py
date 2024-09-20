class DuplicateACKError(Exception):
    def __str__(self):
        return "Duplicate ACK received"
    pass


class TimeoutMaxRetriesError(Exception):
    def __str__(self):
        return "Timeout retries exceeded"
    pass


class ConnectionFailedError(Exception):
    def __str__(self):
        return "Connection to Server Failed"
    pass


class FileNotInServerError(Exception):
    def __str__(self):
        return "File requested not found in Server"
    pass
