from datetime import timedelta
from rate_limiter import RateLimiter


class CircuitBreaker:
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
