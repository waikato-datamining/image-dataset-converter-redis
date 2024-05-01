from typing import List, Dict


def list_classes() -> Dict[str, List[str]]:
    return {
        "seppl.io.Reader": [
            "idc.redis.reader",
        ],
        "seppl.io.Filter": [
            "idc.redis.filter",
        ],
        "seppl.io.Writer": [
            "idc.redis.writer",
        ],
    }
