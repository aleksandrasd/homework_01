from pydantic import BaseModel

from app.shipping.adapter.input.api.v1.shared import CarrierStatus


class GetCarrierStatusesResponse(BaseModel):
    carriers: list[CarrierStatus]
