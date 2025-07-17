from util.steganography import hide_message, reveal_message
from fastapi import HTTPException

class ImageSteganographyService:
    def __init__(self):
        pass

    async def encrypt_image_message(self, image_bytes: bytes, message: str) -> bytes:
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

    async def decrypt_image_message(self, image_bytes: bytes) -> str:
        try:
            extracted_message = reveal_message(image_bytes)
            if not extracted_message:
                return "No se encontró un mensaje oculto o la imagen no fue encriptada con este método."
            return extracted_message
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor al desencriptar: {e}")