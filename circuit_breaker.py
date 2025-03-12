from datetime import timedelta
from rate_limiter import RateLimiter


class CircuitBreaker:
    """
    A circuit breaker implementation using a rate limiter to prevent excessive requests.

    This class helps protect resources from being overwhelmed by limiting the number of
    allowed requests within a specified time window. It utilizes the RateLimiter class
    to enforce request limits and determine when access should be restricted.

    Attributes:
        _resource_id (str): The unique identifier for the resource being protected.
        _rate_limiter (RateLimiter): An instance of the RateLimiter class to track and enforce limits.

    Methods:
        log() -> bool:
            Logs a request to the resource and returns True if the request is allowed,
            or False if the rate limit has been exceeded.

        short_circuit() -> bool:
            Checks if the resource is still accessible based on the rate limit.
            Returns True if access is allowed, False if the limit has been reached.
    """

    def __init__(
        self,
        redis_client,
        resource_id: str,
        number_of_requests: int,
        time_bound: timedelta,
    ):
        self._resource_id = resource_id
        self._rate_limiter = RateLimiter(
            redis_client=redis_client,
            number_of_requests=number_of_requests,
            time_bound=time_bound,
        )

    def log(self) -> bool:
        return self._rate_limiter.log(self._resource_id)

    def short_circuit(self) -> bool:
        return self._rate_limiter.is_allowed(self._resource_id)
