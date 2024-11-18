from pydantic import BaseModel

from app.shipping.domain.entity.shared import annotated


class CarrierEnableStatus(BaseModel):
    carrier: annotated.carrier
    enabled: bool
