import re
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.params import Body
from fastapi.responses import Response
from service.image_service import ImageSteganographyService
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
             summary="Compartir la URL de un video en una imagen",
             response_description="La imagen con la URL del video dentro (PNG).",
             responses={
                 200: {
                     "content": {"image/png": {}},
                     "description": "Retorna la imagen con la URL del video en formato PNG."
                 },
                 400: {"description": "Solicitud inválida."},
                 500: {"description": "Error interno del servidor."}
             }
             )
async def encrypt_image_route(
        image: UploadFile = File(..., description="La imagen PNG/JPG a la que se le incrustará la URL del video."),
        video_url: str = Body(...,
                              description="La URL completa del video a ocultar, e.g., 'http://localhost:8000/api/v1/videos/d6dce7a2-47e9-44b5-801d-0879e59ec068'"),
        steg_service: ImageSteganographyService = Depends(get_image_steganography_service)
):
    """
    Este endpoint permite compartir la URL de un video dentro de una imagen.
    
    - **image**: El archivo de imagen original (JPG, PNG, etc.).
    - **video_url**: La URL completa del endpoint del video que se desea compartir.
    
    Retorna la imagen en formato PNG con la URL dentro.
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo subido no es una imagen válida.")

    ##TODO: Cambiar el prefijo, no solo localhost, pero eso depende del despliegue
    ##Por seguridad actualmente se queda solo en localhost
    uuid_pattern = r"^http://localhost:8000/api/v1/videos/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    if not re.match(uuid_pattern, video_url):
        raise HTTPException(status_code=400, detail="La URL del video proporcionada no tiene el formato esperado.")

    image_bytes = await image.read()

    modified_image_bytes = await steg_service.hide_url(image_bytes, video_url)

    return Response(content=modified_image_bytes, media_type="image/png")


@router.post("/get_video",
             summary="Extraer datos de video de una imagen",
             response_description="Los metadatos del video oculto en la imagen.",
             response_model=VideoInDB,
             responses={
                 400: {"description": "Solicitud inválida."},
                 404: {"description": "No se encontró mensaje o video."},
                 500: {"description": "Error interno del servidor."}
             }
             )
async def decrypt_image_route(
        image: UploadFile = File(..., description="La imagen que contiene la URL del video oculta."),
        steg_service: ImageSteganographyService = Depends(get_image_steganography_service),
        video_service: VideoService = Depends(get_video_service_for_image_route)
):
    """
    Este endpoint permite extraer la URL de un video que fue previamente incrustada
    dentro de una imagen y luego retornar los metadatos de ese video.
    
    - **image**: La imagen (PNG o JPG) que contiene una URL de video dentro.
    
    Retorna los metadatos del video correspondiente a la URL encontrada.
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo subido no es una imagen válida.")

    image_bytes = await image.read()

    video_data = await steg_service.obtain_url(image_bytes, video_service)

    return video_data
