from abc import ABC, abstractmethod

from app.shipping.application.dto.request import TransactionRequestDTO
from app.shipping.application.dto.response import TransactionResponseDTO


class TransactionProcessorUseCase(ABC):
    @abstractmethod
    async def process_transaction(
        self,
        transaction: TransactionRequestDTO,
    ) -> TransactionResponseDTO:
        """Process transaction here"""
