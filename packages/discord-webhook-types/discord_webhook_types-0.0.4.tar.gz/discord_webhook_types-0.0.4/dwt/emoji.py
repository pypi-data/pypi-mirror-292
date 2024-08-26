from typing import NotRequired, TypedDict


class Emoji(TypedDict):
    id: NotRequired[int]
    name: NotRequired[str]
    # roles: NotRequired[Role] # TODO
    roles: NotRequired[dict]
    # user: NotRequired[User] # TODO
    user: NotRequired[dict]
    required_colons: NotRequired[bool]
    managed: NotRequired[bool]
    animated: NotRequired[bool]
    available: NotRequired[bool]
