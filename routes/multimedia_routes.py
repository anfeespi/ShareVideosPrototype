import re
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.params import Body
from fastapi.responses import Response
from service.multimedia_service import ImageSteganographyService
from service.video_service import VideoService
from model.video_model import VideoInDB

router = APIRouter()


async def get_image_steganography_service():
    return ImageSteganographyService()


from config.database import get_database


async def get_video_service_for_image_route():
    db = get_database()
    return VideoService(db["videos"])


@router.post("/share_video",
             summary="Compartir URL de video en imagen, GIF o video",
             response_description="El archivo con la URL del video dentro (PNG).",
             responses={
                 200: {"description": "Retorna el archivo encriptado."},
                 400: {"description": "Solicitud inválida."},
                 500: {"description": "Error interno del servidor."}
             }
             )
async def encrypt_file_route(
        file: UploadFile = File(..., description="El archivo (imagen, GIF o video) a incrustar el mensaje."),
        video_url: str = "http://localhost:8000/api/v1/videos/d6dce7a2-47e9-44b5-801d-0879e59ec068",
        steg_service: ImageSteganographyService = Depends(get_image_steganography_service)
):
    if not file.content_type.startswith(('image/', 'video/')):
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado.")

    file_bytes = await file.read()
    modified_file_bytes = await steg_service.hide_url(file_bytes, file.filename, video_url)

    return Response(content=modified_file_bytes, media_type=file.content_type)


@router.post("/get_video",
             summary="Extraer datos de video de una imagen, GIF o video",
             response_description="Los metadatos del video oculto en la imagen.",
             response_model=VideoInDB,
             responses={
                 400: {"description": "Solicitud inválida."},
                 404: {"description": "No se encontró mensaje o video."},
                 500: {"description": "Error interno del servidor."}
             }
             )
async def decrypt_image_route(
        file: UploadFile = File(..., description="El archivo que contiene la URL del video oculta."),
        steg_service: ImageSteganographyService = Depends(get_image_steganography_service),
        video_service: VideoService = Depends(get_video_service_for_image_route)
):
    """
    Este endpoint permite extraer la URL de un video que fue previamente incrustada
    dentro de una imagen, gif o video y luego retornar los metadatos de ese video.
    
    - **image**: La imagen (PNG o JPG) que contiene una URL de video dentro.
    
    Retorna los metadatos del video correspondiente a la URL encontrada.
    """
    if not file.content_type.startswith(('image/', 'video/')):
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado.")

    file_bytes = await file.read()
    video_data = await steg_service.obtain_url(file_bytes, file.filename, video_service)

    return video_data
