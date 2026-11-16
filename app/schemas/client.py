from pydantic import BaseModel, ConfigDict, Field


class ClientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ClientRead(ClientCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
