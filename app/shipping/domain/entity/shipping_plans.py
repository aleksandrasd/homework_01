from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.shipping.domain.entity.shared import annotated
from app.shipping.domain.service.currency import format_currency_decimal_places


class ShippingPlan(BaseModel):
    carrier: annotated.carrier
    package_size: annotated.package_size
    price: Annotated[Decimal, Field(ge=0)]

    field_validator("price", mode="after")(format_currency_decimal_places)
