from typing import Literal

from pydantic import BaseModel


class GroupBy(BaseModel):
    column: str
    target_column: str
    method: Literal["mean", "median", "max", "min", "sum", "count"] = "mean"
