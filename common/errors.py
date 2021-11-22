from typing import Dict

from fastapi.exceptions import HTTPException


class ValidationError(HTTPException):
    def __init__(
        self,
        detail: Dict
    ) -> None:
        detail = [
            {
                "loc": [
                    k
                ],
                "msg": v,
                "type": "error"
            } for k, v in detail.items()
        ]
        super().__init__(status_code=400, detail=detail)
