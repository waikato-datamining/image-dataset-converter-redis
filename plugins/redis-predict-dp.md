# redis-predict-dp

* accepts: idc.api.DepthData
* generates: idc.api.DepthData

Makes depth information predictions via Redis backend.

```
usage: redis-predict-dp [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [-N LOGGER_NAME] [--skip] [-H REDIS_HOST]
                        [-p REDIS_PORT] [-d REDIS_DB] [-o CHANNEL_OUT]
                        [-i CHANNEL_IN] [-t TIMEOUT] [-a {drop,input}]
                        [-s SLEEP_TIME]
                        [--data_format {grayscale,grayscale-depth,numpy}]

Makes depth information predictions via Redis backend.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -H REDIS_HOST, --redis_host REDIS_HOST
                        The Redis server to connect to. (default: localhost)
  -p REDIS_PORT, --redis_port REDIS_PORT
                        The port the Redis server is running on. (default:
                        6379)
  -d REDIS_DB, --redis_db REDIS_DB
                        The database to use. (default: 0)
  -o CHANNEL_OUT, --channel_out CHANNEL_OUT
                        The Redis channel to send the data out. (default:
                        images)
  -i CHANNEL_IN, --channel_in CHANNEL_IN
                        The Redis channel to receive the data on. (default:
                        predictions)
  -t TIMEOUT, --timeout TIMEOUT
                        The timeout in seconds to wait for a data to arrive.
                        (default: 5.0)
  -a {drop,input}, --timeout_action {drop,input}
                        The action to take when a timeout occurs. (default:
                        drop)
  -s SLEEP_TIME, --sleep_time SLEEP_TIME
                        The time in seconds between polls. (default: 0.01)
  --data_format {grayscale,grayscale-depth,numpy}
                        The data format of the predictions. (default:
                        grayscale)
```
