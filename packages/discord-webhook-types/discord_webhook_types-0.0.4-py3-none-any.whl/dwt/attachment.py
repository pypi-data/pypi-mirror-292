from typing import NotRequired, TypedDict


class Attachment(TypedDict):
    id: int
    filename: str
    title: NotRequired[str]
    description: NotRequired[str]
    content_type: NotRequired[str]
    size: int
    url: str
    proxy_url: str
    height: NotRequired[int]
    width: NotRequired[int]
    ephemeral: NotRequired[bool]
    duration_secs: NotRequired[float]
    waveform: NotRequired[str]
    flags: NotRequired[int]
