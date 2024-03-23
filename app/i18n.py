from typing import Callable

from fastapi import Request


async def get_translation(request: Request) -> Callable[[str], str]:
    return request.state.translation.gettext