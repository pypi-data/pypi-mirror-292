from singer_sdk.streams import RESTStream


class jsonplaceholderStream(RESTStream):
    """A base class for jsonplaceholder API streams."""

    @property
    def url_base(self) -> str:
        return "https://jsonplaceholder.typicode.com"
