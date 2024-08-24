from typing import Any, Dict, List, Literal, TypedDict


class XTSSuccessResponse(TypedDict):
    type: Literal["success", "error"]
    code: str
    description: str
    result: Dict[str, Any] | List[Dict[str, Any]]


class XTSErrorResponse(TypedDict):
    type: Literal["success", "error"]
    code: str
    description: str


XTSResponse = XTSErrorResponse | XTSErrorResponse
