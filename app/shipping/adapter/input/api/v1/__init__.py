from pydantic import BaseModel

from app.shipping.adapter.input.api.v1.shared import CarrierStatus


class GetCarriersResponse(BaseModel):
    carriers: list[CarrierStatus]
