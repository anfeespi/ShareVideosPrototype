from uuid import UUID

from util.steganography import hide_message, reveal_message
import re
from fastapi import HTTPException
from service.video_service import VideoService
from model.video_model import VideoInDB

class ImageSteganographyService:
    def __init__(self):
        pass

    async def hide_url(self, image_bytes: bytes, message: str) -> bytes:
        try:
            if not message:
                raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")
            if len(message) > 5000:
                raise HTTPException(status_code=400, detail="El mensaje es demasiado largo.")

            modified_image_bytes = hide_message(image_bytes, message)
            return modified_image_bytes
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor al encriptar: {e}")

    async def obtain_url(self, image_bytes: bytes, video_service: VideoService) -> VideoInDB:
        try:
            extracted_url = reveal_message(image_bytes)

            if not extracted_url:
                raise HTTPException(status_code=404, detail="No hay un video o link válido.")

            uuid_pattern = r".*/api/v1/videos/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$"
            match = re.match(uuid_pattern, extracted_url)

            if not match:
                raise HTTPException(status_code=400, detail="No es una URL de video válida o está en un formato incorrecto.")

            video_uuid_str = match.group(1)

            video_data = await video_service.get_video_by_uuid(UUID(video_uuid_str))

            if not video_data:
                raise HTTPException(status_code=404, detail=f"Video con UUID '{video_uuid_str}' no encontrado.")

            return video_data

        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"UUID inválido en la URL: {e}")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor al obtener el video: {e}")
