Changelog
=========

0.0.5 (????-??-??)
------------------

- switched to `kasperl` library for base API and generic pipeline plugins


0.0.4 (2025-07-11)
------------------

- using new prefixed image segmentation methods like `imgseg_from_bluechannel` instead of `to_bluechannel`
- added `redis-predict-dp` filter for taking advantage of depth estimation docker images
- the redis-predict-dp/-ic/-is/-od filters now set the image_name as well when creating the new container


0.0.3 (2025-04-03)
------------------

- switched to underscores in project name
- `redis-predict-od` info clarifies that predictions are made in OPEX format


0.0.2 (2024-06-13)
------------------

- messages regarding timeouts now use WARNING instead of INFO (pubsub filter/listener reader)


0.0.1 (2024-05-06)
------------------

- initial release

