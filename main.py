from fastapi import FastAPI
from contextlib import asynccontextmanager
from config.database import mongo_connect, mongo_disconnect
from routes import video_routes, image_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo_connect()
    yield
    await mongo_disconnect()

app = FastAPI(
    title="Prototipo de funcionalidad para compartir videos",
    description="Una API de prueba para la función de compartir videos por medio de imágenes",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.include_router(video_routes.router, prefix="/api/v1/videos", tags=["Videos"])

app.include_router(image_routes.router, prefix="/api/v1/steganography", tags=["Images"])

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de prueba. Visita /docs para la documentación interactiva."}