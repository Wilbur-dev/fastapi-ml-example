from fastapi import FastAPI
from app.api.routes.router import api
from app.core.lifecycle import lifespan

from app.observability.exception_handlers import register_exception_handlers

def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(api)
    
    register_exception_handlers(app)
    
    return app

app = get_app()

