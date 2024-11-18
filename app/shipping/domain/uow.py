from abc import ABC, abstractmethod

import typing_extensions as t

if t.TYPE_CHECKING:
    UnitOfWorkMixinBase: t.TypeAlias = "UnitOfWorkHost"
else:
    UnitOfWorkMixinBase = object


class UnitOfWorkHost(ABC):
    @abstractmethod
    async def begin(self) -> None: ...
    @abstractmethod
    async def abort(self) -> None: ...
    @abstractmethod
    async def commit(self) -> None: ...


class UnitOfWorkMixin(UnitOfWorkMixinBase):
    async def __aenter__(self) -> None:
        await self.begin()

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type:
            await self.abort()
        else:
            await self.commit()


class UnitOfWork(UnitOfWorkMixin, UnitOfWorkHost):
    pass
