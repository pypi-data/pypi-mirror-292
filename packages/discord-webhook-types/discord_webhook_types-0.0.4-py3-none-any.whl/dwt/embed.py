from typing import NotRequired, TypedDict


class EmbedFooter(TypedDict):
    text: str
    icon_url: NotRequired[str]
    proxy_icon_url: NotRequired[str]


class EmbedImage(TypedDict):
    url: str
    proxy_url: NotRequired[str]
    height: NotRequired[int]
    width: NotRequired[int]


class EmbedThumbnail(TypedDict):
    url: str
    proxy_url: NotRequired[str]
    height: NotRequired[int]
    width: NotRequired[int]


class EmbedVideo(TypedDict):
    url: NotRequired[str]
    proxy_url: NotRequired[str]
    height: NotRequired[int]
    width: NotRequired[int]


class EmbedProvider(TypedDict):
    name: NotRequired[str]
    url: NotRequired[str]


class EmbedAuthor(TypedDict):
    name: str
    url: NotRequired[str]
    icon_url: NotRequired[str]
    proxy_icon_url: NotRequired[str]


class EmbedField(TypedDict):
    name: str
    value: str
    inline: NotRequired[bool]


class Embed(TypedDict):
    title: NotRequired[str]
    type: NotRequired[str]
    description: NotRequired[str]
    url: NotRequired[str]
    timestamp: NotRequired[str]
    color: NotRequired[int]
    footer: NotRequired[EmbedFooter]
    image: NotRequired[EmbedImage]
    thumbnail: NotRequired[EmbedThumbnail]
    video: NotRequired[EmbedVideo]
    provider: NotRequired[EmbedProvider]
    author: NotRequired[EmbedAuthor]
    fields: NotRequired[list[EmbedField]]
