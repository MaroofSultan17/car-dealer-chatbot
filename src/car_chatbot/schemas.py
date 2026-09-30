from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ApiDto(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class CarSearchRequestDto(ApiDto):
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=500)


class DealerResponseDto(ApiDto):
    dealer_id: str
    name: str
    phone: str
    email: str
    city: str


class CarResponseDto(ApiDto):
    car_id: str
    make: str
    model: str
    variant: str
    year: int
    price_in_cents: int
    dealer: DealerResponseDto | None


class NoticeResponseDto(ApiDto):
    level: Literal["info", "warning"]
    text: str


class CarSearchResponseDto(ApiDto):
    cars: list[CarResponseDto]
    notices: list[NoticeResponseDto]
