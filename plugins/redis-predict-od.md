# redis-predict-od

* accepts: idc.api.ObjectDetectionData
* generates: idc.api.ObjectDetectionData

Makes object detection predictions via Redis backend.

```
usage: redis-predict-od [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [-N LOGGER_NAME] [-H REDIS_HOST] [-p REDIS_PORT]
                        [-d REDIS_DB] [-o CHANNEL_OUT] [-i CHANNEL_IN]
                        [-t TIMEOUT] [-s SLEEP_TIME] [--key_label KEY_LABEL]
                        [--key_score KEY_SCORE]

Makes object detection predictions via Redis backend.

optional arguments:
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
                        The Redis channel to send the images out. (default:
                        images)
  -i CHANNEL_IN, --channel_in CHANNEL_IN
                        The Redis channel to receive the predictions on.
                        (default: predictions)
  -t TIMEOUT, --timeout TIMEOUT
                        The timeout in seconds to wait for a prediction to
                        arrive. (default: 5.0)
  -s SLEEP_TIME, --sleep_time SLEEP_TIME
                        The time in seconds between polls. (default: 0.01)
  --key_label KEY_LABEL
                        The key in the metadata for the storing the label.
                        (default: type)
  --key_score KEY_SCORE
                        The key in the metadata for the storing the score.
                        (default: score)
```
