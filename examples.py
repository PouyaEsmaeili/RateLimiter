import os
from redis import StrictRedis
from circuit_breaker import CircuitBreaker
from rate_limiter import RateLimiter
from datetime import timedelta


USER_MSG = (
    "Sorry, you have exceeded the maximum number of attempts. Please try again later."
)
CIRCUIT_BREAKER_MSG = "Circuit breaker triggered: Notification system temporarily disabled to prevent flooding."

redis_client = StrictRedis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
)
rate_limiter = RateLimiter(
    redis_client=redis_client, number_of_requests=5, time_bound=timedelta(60)
)
circuit_breaker = CircuitBreaker(
    redis_client=redis_client,
    resource_id="AlarmingSystem",
    number_of_requests=10,
    time_bound=timedelta(60),
)


# Example1: Limit number of attempts to reset password in a web application
def forget_password(email):
    assert rate_limiter.log(resource_id="FORGET_PASSWORD", client_id=email) is True, (
        USER_MSG
    )
    # Password recovery logic here


# Example2: Short circuit alarming system to avoid notification flooding
def send_error_notification(error_msg):
    assert circuit_breaker.log() is True, CIRCUIT_BREAKER_MSG
    # Send notification here
