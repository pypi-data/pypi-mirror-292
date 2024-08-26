from typing import NotRequired, TypedDict
from dwt.emoji import Emoji


class PollMedia(TypedDict):
    text: NotRequired[str]
    emoji: NotRequired[Emoji]


class PollAnswer(TypedDict):
    answer_id: NotRequired[int]
    poll_media: PollMedia


class Poll(TypedDict):
    question: PollMedia
    answers: list[PollAnswer]
    duration: NotRequired[int]
    allow_multiselect: NotRequired[bool]
    layout_type: NotRequired[int]
