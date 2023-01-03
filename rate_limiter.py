from datetime import timedelta
from random import choices
from redis import StrictRedis
from string import ascii_uppercase, ascii_lowercase


class RateLimiter(object):
    def __init__(self,
                 con_pool: StrictRedis,
                 number_of_requests: int,
                 time_bound: timedelta,
                 limit_per_client: bool = False,
                 lock_timeout: float = 0.1,
                 log_value: str = ''):
        self._con_pool = con_pool
        self._number_of_requests = number_of_requests
        self._time_bound = time_bound
        self._limit_per_client = limit_per_client
        self._lock_timeout = lock_timeout
        self._log_value = log_value

    def _get_lock_name(self, client_id: str, resource_id: str) -> str:
        if self._limit_per_client:
            return f'{resource_id}-lock'
        return f'{client_id}-{resource_id}-lock'

    def _get_log_pattern(self, client_id: str, resource_id: str) -> str:
        if self._limit_per_client:
            return f'{resource_id}-*'
        return f'{client_id}-{resource_id}-*'

    def _generate_log_name(self, client_id: str, resource_id: str) -> str:
        padding = ''.join(
            choices(
                ascii_uppercase + ascii_lowercase,
                k=10,
            )
        )
        if self._limit_per_client:
            return f'{resource_id}-{padding}'
        return f'{client_id}-{resource_id}-{padding}'

    def log(self, client_id: str, resource_id: str) -> bool:
        lock_name = self._get_lock_name(client_id, resource_id)
        with self._con_pool.lock(name=lock_name, timeout=self._lock_timeout):
            if self.is_allowed(client_id, resource_id):
                log_name = self._generate_log_name(client_id, resource_id)
                self._con_pool.setex(
                    name=log_name,
                    time=self._time_bound,
                    value=self._log_value
                )
                return True
        return False

    def is_allowed(self, client_id: str, resource_id: str) -> bool:
        num_logs = self.count_logs(client_id, resource_id)
        return num_logs <= self._number_of_requests

    def count_logs(self, client_id: str, resource_id: str) -> int:
        log_pattern = self._get_log_pattern(client_id, resource_id)
        return len(self._con_pool.keys(log_pattern))

    def flush_logs(self, client_id: str, resource_id: str) -> None:
        log_pattern = self._get_log_pattern(client_id, resource_id)
        self._con_pool.delete(log_pattern)
