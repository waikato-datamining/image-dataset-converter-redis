# redis-data-broadcast

* accepts: idc.api.ImageData

Broadcasts the incoming data on the specified channel.

```
usage: redis-data-broadcast [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                            [-N LOGGER_NAME] [-H REDIS_HOST] [-p REDIS_PORT]
                            [-d REDIS_DB] [-o CHANNEL_OUT] [-i]

Broadcasts the incoming data on the specified channel.

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
  -o CHANNEL_OUT, --channel_out CHANNEL_OUT
                        The Redis channel to broadcast the data on. (default:
                        data_out)
  -i, --include_image   Whether to send the image as well. (default: False)
```
