from fastapi import APIRouter, Depends, status

from app.container import Container
from app.shipping.adapter.input.api.v1.request import SetCarrierStatusRequest
from app.shipping.adapter.input.api.v1.response import (
    GetCarrierStatusesResponse,
)
from app.shipping.domain.usecase.carrier import CarrierUseCase

carrier_router = APIRouter()


@carrier_router.get("", response_model=GetCarrierStatusesResponse)
async def get_carrier_statuses(
    usecase: CarrierUseCase = Depends(Container.get_carrier_manager_usecase),
):
    carrier_statuses = await usecase.get_enable_statuses()
    carriers = []

    for carrier_status in carrier_statuses:
        carriers.append(
            {"code": carrier_status.carrier, "enabled": carrier_status.enabled}
        )

    return {"carriers": carriers}


@carrier_router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def set_carrier_status(
    request: SetCarrierStatusRequest,
    usecase: CarrierUseCase = Depends(Container.get_carrier_manager_usecase),
):
    await usecase.set_enabled(request.code, enabled=request.enabled)
