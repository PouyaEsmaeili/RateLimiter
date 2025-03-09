# Implementation of Rate Limiter with Redis

A Rate Limiter controls and restricts the rate at which requests can access an object or resource. 
This limit is typically measured in units such as Requests Per Second (RPS) or Requests Per Minute (RPM). 
The primary purpose of using a Rate Limiter is to ensure resources remain available and to prevent Denial of Service (DoS) attacks. 
One popular algorithm for implementing Rate Limiting is the Leaky Bucket algorithm. 
In this repository, the Leaky Bucket algorithm is implemented using the Redis cache engine.

* Learn more about leaky bucket [here](https://en.wikipedia.org/wiki/Leaky_bucket).

* For more details about this implementation read my blog post [here](https://medium.com/@pouya.esmaeili.g/rate-limiter-with-redis-ac6913932bf5).


# Circuit Breaker:

As an example, a simple Circuit Breaker has been implemented using the Leaky Bucket Rate Limiter. 
To understand how a Circuit Breaker works, read Martin Fowler's article [here](https://martinfowler.com/bliki/CircuitBreaker.html).

## Activate Env

```commandline
uv sync
```
--> [UV installation guide](https://docs.astral.sh/uv/getting-started/installation/)

## Linting with Ruff 

```commandline
ruff format --check
```
```commandline
ruff check
```


### TODO list:

- Implementation of async version
- Implementation of other methods of rate limiting
