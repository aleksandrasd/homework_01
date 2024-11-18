from fastapi import APIRouter, Depends

from app.container import Container
from app.shipping.application.dto.request import TransactionRequestDTO
from app.shipping.application.dto.response import TransactionResponseDTO
from app.shipping.application.service.transaction import TransactionProcessor

transaction_router = APIRouter()


@transaction_router.post("", response_model=TransactionResponseDTO)
async def get_user_list(
    request: TransactionRequestDTO,
    usecase: TransactionProcessor = Depends(
        Container.get_transaction_processor_usecase
    ),
):
    return await usecase.process_transaction(request)
