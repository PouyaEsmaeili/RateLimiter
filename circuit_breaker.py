import os
from datetime import timedelta
from redis import StrictRedis, ConnectionPool
from .rate_limiter import RateLimiter


class CircuitBreaker:

    def __init__(self, resource_id: str, number_of_requests: int, time_bound: timedelta):
        self._resource_id = resource_id
        conn_pool = ConnectionPool(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=0,
        )
        redis_client = StrictRedis(connection_pool=conn_pool)
        self._rate_limiter = RateLimiter(
            con_pool=redis_client,
            number_of_requests=number_of_requests,
            time_bound=time_bound,
        )

    def log(self) -> bool:
        return self._rate_limiter.log(self._resource_id)

    def short_circuit(self) -> bool:
        return self._rate_limiter.is_allowed(self._resource_id)
