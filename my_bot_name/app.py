from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from my_bot_name.routers import alive, health


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


def get_app():
    """
    Create and configure a FastAPI application

    Returns:
        FastAPI: A configured instance of the FastAPI application.

    """
    app_ = FastAPI()

    # Configurazione CORS
    app_.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "*"
        ],  # Consente tutte le origini. In produzione, specificare i domini consentiti
        allow_credentials=True,
        allow_methods=["*"],  # Consente tutti i metodi HTTP
        allow_headers=["*"],  # Consente tutti gli headers
        expose_headers=["*"],
        max_age=600,  # Tempo in secondi per cui il browser può cachare la risposta del preflight
    )

    app_.include_router(router=alive.router)
    app_.include_router(router=health.router)

    return app_


app = get_app()


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a raibow..."},
    )
