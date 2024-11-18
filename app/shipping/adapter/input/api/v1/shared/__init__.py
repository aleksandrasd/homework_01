from pydantic import BaseModel

from app.shipping.domain.entity.shared import annotated


class CarrierStatus(BaseModel):
    code: annotated.carrier
    enabled: bool
