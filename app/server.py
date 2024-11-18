from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.shipping.adapter.input import router
from core.exceptions import CustomException


def init_routers(app_: FastAPI) -> None:
    app_.include_router(router)


def init_listeners(app_: FastAPI) -> None:
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content=exc.message,
        )


def build_app() -> FastAPI:
    app_ = FastAPI()
    init_routers(app_=app_)
    init_listeners(app_=app_)
    return app_
