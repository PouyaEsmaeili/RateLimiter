import pytest
from datetime import timedelta
from rate_limiter import RateLimiter


NUMBER_OF_REQUESTS = 5


class FakeRedis:

    def __init__(self):
        self._repo = list()
        self._limit = NUMBER_OF_REQUESTS

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def __enter__(self):
        return self

    def lock(self, *args, **kwargs):
        return self

    def setex(self, *args, **kwargs) -> None:
        self._repo.append("dummy")

    def keys(self, *args, **kwargs) -> list[str]:
        return self._repo

    def delete(self, *args, **kwargs) -> None:
        self._repo = list()


@pytest.fixture
def redis_client():
    return FakeRedis()


@pytest.fixture
def rate_limiter(redis_client):
    return RateLimiter(
        redis_client,
        number_of_requests=NUMBER_OF_REQUESTS,
        time_bound=timedelta(seconds=10),
    )


def test_log_allows_requests_within_limit(rate_limiter):
    resource_id = "test_resource"
    client_id = "test_client"

    for _ in range(NUMBER_OF_REQUESTS + 1):
        assert rate_limiter.log(resource_id, client_id) is True

    assert rate_limiter.log(resource_id, client_id) is False


def test_flush_logs(rate_limiter):
    resource_id = "test_resource"
    client_id = "test_client"

    rate_limiter.log(resource_id, client_id)
    rate_limiter.flush_logs(resource_id, client_id)

    assert rate_limiter.count_logs(resource_id, client_id) == 0
