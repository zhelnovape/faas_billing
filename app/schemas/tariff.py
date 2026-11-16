from decimal import Decimal

from pydantic import BaseModel, Field


class TariffCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    price_per_call: Decimal = Field(default=Decimal(0), ge=0)
    price_per_ms: Decimal = Field(default=Decimal(0), ge=0)
    price_per_gb_second: Decimal = Field(default=Decimal(0), ge=0)
    cold_start_surcharge: Decimal = Field(default=Decimal(0), ge=0)


class TariffRead(TariffCreate):
    id: int
