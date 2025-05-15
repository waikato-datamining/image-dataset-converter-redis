# redis-image-listen

* generates: idc.api.ImageData

Listens for images being broadcast and forwards them as the specified data type.

```
usage: redis-image-listen [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                          [-N LOGGER_NAME] [-H REDIS_HOST] [-p REDIS_PORT]
                          [-d REDIS_DB] [-i CHANNEL_IN] [-t TIMEOUT]
                          [-a {keep-waiting,stop}] [-s SLEEP_TIME] -T
                          {dp,ic,is,od} [-P PREFIX]

Listens for images being broadcast and forwards them as the specified data
type.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -H REDIS_HOST, --redis_host REDIS_HOST
                        The Redis server to connect to. (default: localhost)
  -p REDIS_PORT, --redis_port REDIS_PORT
                        The port the Redis server is running on. (default:
                        6379)
  -d REDIS_DB, --redis_db REDIS_DB
                        The database to use. (default: 0)
  -i CHANNEL_IN, --channel_in CHANNEL_IN
                        The Redis channel to receive the data on. (default:
                        data_in)
  -t TIMEOUT, --timeout TIMEOUT
                        The timeout in seconds to wait for a data to arrive.
                        (default: 30.0)
  -a {keep-waiting,stop}, --timeout_action {keep-waiting,stop}
                        The action to take when a timeout occurs. (default:
                        keep-waiting)
  -s SLEEP_TIME, --sleep_time SLEEP_TIME
                        The time in seconds between polls. (default: 0.01)
  -T {dp,ic,is,od}, --data_type {dp,ic,is,od}
                        The type of data to forward (default: None)
  -P PREFIX, --prefix PREFIX
                        The prefix to use for the images (default: None)
```

The following data types are available:

* dp: depth
* ic: image classification
* is: image segmentation
* od: object detection

