import abc


class BaseLock(abc.ABC):
    @abc.abstractmethod
    def acquire(self) -> None:
        """Acquire the lock."""

    @abc.abstractmethod
    def release(self) -> None:
        """Releases the lock.

        Raises:
          LockNotOwnedException: if attempting to release lock when lock is no
                                 longer owned.
        """

    @abc.abstractmethod
    def reacquire(self) -> None:
        """Resets a TTL of an already acquired lock back to a timeout value.

        Raises:
          LockNotOwnedException: if attempting to reacquire when lock is no
                                longer owned.
        """
