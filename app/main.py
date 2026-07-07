from fastapi import FastAPI

from app.error_handlers import register_exception_handlers
from app.routers import materials, warehouses

app = FastAPI(
    title="My Material Movement Producer Service✨",
)

register_exception_handlers(app)

app.include_router(warehouses.router)
app.include_router(materials.router)
