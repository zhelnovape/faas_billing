from pydantic import BaseModel, ConfigDict, Field


class FunctionCreate(BaseModel):
    client_id: int
    tariff_id: int
    name: str = Field(min_length=1, max_length=255)


class FunctionRead(FunctionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
