from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import Response
from service.image_service import ImageSteganographyService

router = APIRouter()

async def get_image_steganography_service():
    return ImageSteganographyService()

@router.post("/share",
             summary="Ocultar texto dentro de una imagen",
             response_description="La imagen con el mensaje oculto (PNG).",
             responses={
                 200: {
                     "content": {"image/png": {}},
                     "description": "Retorna la imagen encriptada en formato PNG."
                 },
                 400: {"description": "Solicitud inválida."},
                 500: {"description": "Error interno del servidor."}
             }
             )
async def encrypt_image_route(
        image: UploadFile = File(..., description="La imagen PNG/JPG a la que se le incrustará el mensaje."),
        message: str = "Texto a incluir",
        steg_service: ImageSteganographyService = Depends(get_image_steganography_service)
):
    """
    Incluir un mensaje/link dentro de una imagen seleccionada

    - **image**: El archivo de imagen original (JPG, PNG, etc.).
    - **message**: El texto que para incluir dentro de la imagen.

    Retorna la imagen modificada en formato PNG con el mensaje oculto.
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo subido no es una imagen válida.")

    image_bytes = await image.read()

    modified_image_bytes = await steg_service.encrypt_image_message(image_bytes, message)

    return Response(content=modified_image_bytes, media_type="image/png")


@router.post("/obtain",
             summary="Obtener texto de una imagen",
             response_description="El mensaje oculto en la imagen.",
             response_model=dict  # Indicamos que la respuesta es un JSON con el mensaje
             )
async def decrypt_image_route(
        image: UploadFile = File(..., description="La imagen que contiene el mensaje oculto."),
        steg_service: ImageSteganographyService = Depends(get_image_steganography_service)
):
    """
    Este endpoint permite extraer un mensaje de texto que fue previamente ocultado
    dentro de una imagen usando este mismo servicio.

    - **image**: La imagen (PNG o JPG) que se supone contiene un mensaje oculto.

    Retorna el mensaje de texto que se encontró.
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo subido no es una imagen válida.")

    image_bytes = await image.read()
    extracted_message = await steg_service.decrypt_image_message(image_bytes)

    return {"message": extracted_message}