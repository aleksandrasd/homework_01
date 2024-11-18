import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.shipping.domain.entity.shared import annotated
from app.shipping.domain.service.currency import format_currency_decimal_places


class UnprocessedTransaction(BaseModel):
    date: datetime.date
    package_size: annotated.package_size
    carrier: annotated.carrier


class ProcessedTransaction(UnprocessedTransaction, BaseModel):
    discount_id: int | None
    discount: Annotated[Decimal | None, Field(ge=0)]

    field_validator("discount", mode="after")(format_currency_decimal_places)
