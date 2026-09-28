from pydantic import BaseModel


class CarSearch(BaseModel):
    make: str | None = None
    model: str | None = None
    variant: str | None = None