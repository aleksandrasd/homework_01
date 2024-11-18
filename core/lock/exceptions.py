class LockNotOwnedException(Exception):
    """
    Exception raised when an operation is attempted on a lock that is
    not owned by the current entity (e.g. attempting to releasing lock without
    being owner of the lock).
    """
