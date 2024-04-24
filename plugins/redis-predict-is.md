# redis-predict-is

* accepts: idc.api.ImageSegmentationData
* generates: idc.api.ImageSegmentationData

Makes image segmentation predictions via Redis backend.

```
usage: redis-predict-is [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [-N LOGGER_NAME] [-H REDIS_HOST] [-p REDIS_PORT]
                        [-d REDIS_DB] [-o CHANNEL_OUT] [-i CHANNEL_IN]
                        [-t TIMEOUT] [-a {drop,input}] [-s SLEEP_TIME]
                        [--image_format {indexedpng,bluechannel,grayscale}]
                        [--labels LABEL [LABEL ...]]

Makes image segmentation predictions via Redis backend.

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
  --image_format {indexedpng,bluechannel,grayscale}
                        The image format of the predictions. (default:
                        indexedpng)
  --labels LABEL [LABEL ...]
                        The labels that the indices represent. (default: None)
```
