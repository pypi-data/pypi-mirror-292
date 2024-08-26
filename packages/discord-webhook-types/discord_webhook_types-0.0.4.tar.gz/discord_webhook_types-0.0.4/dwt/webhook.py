from typing import NotRequired, TypedDict

from dwt.allowed_mention import AllowedMention
from dwt.attachment import Attachment
from dwt.component import Component
from dwt.embed import Embed
from dwt.poll import Poll


class WebHook(TypedDict):
    content: NotRequired[str]
    username: NotRequired[str]
    avatar_url: NotRequired[str]
    tts: NotRequired[bool]
    embeds: NotRequired[list[Embed]]
    allowed_mentions: NotRequired[list[AllowedMention]]
    components: NotRequired[list[Component]]
    files: NotRequired[list[str]]
    payload_json: NotRequired[str]
    attachments: NotRequired[list[Attachment]]
    flags: NotRequired[int]
    thread_name: NotRequired[str]
    applied_tags: NotRequired[str]
    poll: NotRequired[Poll]
