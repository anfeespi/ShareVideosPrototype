import io
from uuid import UUID

import imageio
from moviepy import VideoFileClip, ImageSequenceClip

from util.steganography import hide_message_image, hide_message_in_frames, reveal_message_image, \
    reveal_message_from_frames
import re
from fastapi import HTTPException
from service.video_service import VideoService
from model.video_model import VideoInDB

class ImageSteganographyService:
    def __init__(self):
        pass

    async def hide_url(self, file_bytes: bytes, filename: str, message: str) -> bytes:
        try:
            if not message:
                raise HTTPException(status_code=400, detail="La url no puede estar vacía.")
            if len(message) > 5000:
                raise HTTPException(status_code=400, detail="La url es demasiado larga.")

            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                return hide_message_image(file_bytes, message)
            elif filename.lower().endswith('.gif'):
                # Lógica para GIF
                gif_reader = imageio.get_reader(io.BytesIO(file_bytes))
                frames = [frame for frame in gif_reader]
                new_frames = hide_message_in_frames(frames, message)

                output_buffer = io.BytesIO()
                imageio.mimsave(output_buffer, new_frames, format='GIF')
                output_buffer.seek(0)
                return output_buffer.getvalue()
            elif filename.lower().endswith(('.mp4', '.avi', '.mov')):
                with open("temp_input_video", "wb") as f:
                    f.write(file_bytes)
                clip = VideoFileClip("temp_input_video")
                frames = list(clip.iter_frames())

                new_frames = hide_message_in_frames(frames, message)

                new_clip = ImageSequenceClip(new_frames, fps=clip.fps)
                output_buffer = io.BytesIO()
                new_clip.write_videofile("temp_output_video.mp4", codec="libx264", audio_codec="aac")

                with open("temp_output_video.mp4", "rb") as f:
                    output_bytes = f.read()
                import os
                os.remove("temp_input_video")
                os.remove("temp_output_video.mp4")

                return output_bytes
            else:
                raise HTTPException(status_code=400, detail="Formato de archivo no soportado.")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor al encriptar: {e}")

    async def obtain_url(self, file_bytes: bytes, filename: str, video_service: VideoService) -> VideoInDB:
        try:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                extracted_url = reveal_message_image(file_bytes)
            elif filename.lower().endswith('.gif'):
                gif_reader = imageio.get_reader(io.BytesIO(file_bytes))
                frames = [frame for frame in gif_reader]
                extracted_url = reveal_message_from_frames(frames)
            elif filename.lower().endswith(('.mp4', '.avi', '.mov')):
                with open("temp_input_video", "wb") as f:
                    f.write(file_bytes)
                clip = VideoFileClip("temp_input_video")
                frames = list(clip.iter_frames())
                extracted_url = reveal_message_from_frames(frames)
                import os
                os.remove("temp_input_video")
            else:
                raise HTTPException(status_code=400, detail="Formato de archivo no soportado.")

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