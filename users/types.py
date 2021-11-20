from datetime import datetime
from typing import TypedDict


class JwtData(TypedDict, total=False):
    user_id: int
    expire: datetime
