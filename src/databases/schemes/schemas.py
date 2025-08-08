import datetime

from pydantic import BaseModel, field_validator


class Cabin(BaseModel):
    id: int | None = None
    number: int
    hex_color: str

    @field_validator('hex_color')
    def check_hex(cls, v):
        if not (isinstance(v, str) and v.startswith("#") and len(v) == 7):
            raise ValueError("Hex color must be in format #RRGGBB")
        return v

    class Config:
        from_attributes = True


class Operator(BaseModel):
    id: int | None = None
    name: str

    class Config:
        from_attributes = True


class WorkingTimes(BaseModel):
    id: int | None = None
    min_start_time: datetime.time
    max_finish_time: datetime.time

    class Config:
        from_attributes = True
