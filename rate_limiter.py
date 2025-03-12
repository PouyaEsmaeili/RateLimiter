from datetime import timedelta
from random import choices
from redis import StrictRedis
from string import ascii_uppercase, ascii_lowercase


class RateLimiter(object):
    """
    A rate limiter implementation based on Redis using the leaky bucket algorithm.

    This class limits the number of requests a client can make to a specific resource
    within a defined time period. It supports both client-specific rate limiting (when client_id is provided)
    and global rate limiting (when client_id is not provided) for resources.

    Attributes:
        redis_client (StrictRedis): The Redis connection pool used for Redis operations.
        number_of_requests (int): The maximum number of allowed requests within the time_bound period.
        time_bound (timedelta): The time window within which the requests are counted.
        lock_timeout (float): Timeout in seconds for acquiring a lock to prevent race conditions.
        log_value (str): The value to store in Redis when logging a request.

    Methods:
        log(resource_id: str, client_id: str | None = None) -> bool:
            Logs a request for the resource (and optionally client) if the rate limit is not exceeded.
            Returns True if allowed, False otherwise.

        is_allowed(resource_id: str, client_id: str | None = None) -> bool:
            Checks if a client (or globally) is allowed to make a request to a resource based on the rate limit.

        count_logs(resource_id: str, client_id: str | None = None) -> int:
            Counts the number of logs associated with a client and resource in Redis, considering global or client-specific limits.

        flush_logs(resource_id: str, client_id: str | None = None) -> None:
            Removes all logs related to a client and resource from Redis, resetting the rate limit.

    Private Methods:
        _get_lock_name(resource_id: str, client_id: str | None = None) -> str:
            Generates a unique lock name based on the resource (and optionally client ID) to ensure atomic operations.

        _get_log_pattern(resource_id: str, client_id: str | None = None) -> str:
            Generates the log pattern for counting logs in Redis, considering whether the limit is global or client-specific.

        _generate_log_name(resource_id: str, client_id: str | None = None) -> str:
            Generates a unique log name with a random padding string to ensure uniqueness of logs.
    """

    def __init__(
        self,
        redis_client: StrictRedis,
        number_of_requests: int,
        time_bound: timedelta,
        lock_timeout: float = 0.1,
        log_value: str = "",
    ):
        self._redis_client = redis_client
        self._number_of_requests = number_of_requests
        self._time_bound = time_bound
        self._lock_timeout = lock_timeout
        self._log_value = log_value

    def _get_lock_name(self, resource_id: str, client_id: str | None = None) -> str:
        if client_id:
            return f"{client_id}-{resource_id}-lock"
        return f"{resource_id}-lock"

    def _get_log_pattern(self, resource_id: str, client_id: str | None = None) -> str:
        if client_id:
            return f"{client_id}-{resource_id}-*"
        return f"{resource_id}-*"

    def _generate_log_name(self, resource_id: str, client_id: str | None = None) -> str:
        padding = "".join(
            choices(
                ascii_uppercase + ascii_lowercase,
                k=10,
            )
        )
        if client_id:
            return f"{client_id}-{resource_id}-{padding}"
        return f"{resource_id}-{padding}"

    def log(self, resource_id: str, client_id: str | None = None) -> bool:
        lock_name = self._get_lock_name(client_id, resource_id)
        with self._redis_client.lock(name=lock_name, timeout=self._lock_timeout):
            if self.is_allowed(client_id, resource_id):
                log_name = self._generate_log_name(client_id, resource_id)
                self._redis_client.setex(
                    name=log_name, time=self._time_bound, value=self._log_value
                )
                return True
        return False

    def is_allowed(self, resource_id: str, client_id: str | None = None) -> bool:
        num_logs = self.count_logs(client_id, resource_id)
        return num_logs <= self._number_of_requests

    def count_logs(self, resource_id: str, client_id: str | None = None) -> int:
        log_pattern = self._get_log_pattern(client_id, resource_id)
        return len(self._redis_client.keys(log_pattern))

    def flush_logs(self, resource_id: str, client_id: str | None = None) -> None:
        log_pattern = self._get_log_pattern(client_id, resource_id)
        self._redis_client.delete(log_pattern)
