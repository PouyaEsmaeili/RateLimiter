# Implementation of Rate Limiter with Redis

Rate Limiter, controls and limits the rate of requests to access an object or resource.
This limitation is mostly represented by units like Requests Per Seconds (RPS) or Requests Per Minutes (RPM). 
The reason to use Rate Limiter is to maintain the resources available and prevent denial of service (DoS). 
One of the common algorithms to implement Rate Limiter is Leaky Bucket. 
In this repository, the Leaky Bucket is implemented based on Redis cache engine.

Read more about leaky bucket from [here](https://en.wikipedia.org/wiki/Leaky_bucket).


### TODO list:

- Implementation of async version
