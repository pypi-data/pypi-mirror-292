from typing import List
from singer_sdk import Tap, Stream
from tap_oviond.streams import CommentsStream

STREAM_TYPES = [CommentsStream]


class TapOviond(Tap):
    name = "tap-oviond"

    def discover_streams(self) -> List[Stream]:
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
