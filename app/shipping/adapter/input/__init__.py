from fastapi import APIRouter

from app.shipping.adapter.input.api.v1.carrier import (
    carrier_router as carrier_v1_router,
)
from app.shipping.adapter.input.api.v1.transaction import (
    transaction_router as transaction_v1_router,
)

router = APIRouter()
router.include_router(transaction_v1_router, prefix="/transactions")
router.include_router(carrier_v1_router, prefix="/carriers")

__all__ = ["router"]
