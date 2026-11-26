from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    status: str = "success"
    data: Optional[T] = None
