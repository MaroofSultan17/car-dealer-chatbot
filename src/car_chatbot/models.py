from pydantic import BaseModel, Field


class CarSearch(BaseModel):
    make: str | None = None
    model: str | None = None
    variant: str | None = None
    preferences: list[str] = Field(default_factory=list)


class CarRecommendations(BaseModel):
    car_ids: list[str] = Field(default_factory=list)