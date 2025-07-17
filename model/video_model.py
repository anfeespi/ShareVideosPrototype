from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info):
        if not ObjectId.is_valid(v):
            raise ValueError("ID de objeto inválido")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: type, handler) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.with_info_plain_validator_function(cls.validate),
            serialization=core_schema.to_string_ser_schema(),
        )

# DTO
class VideoCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Título del video.")
    description: Optional[str] = Field(None, max_length=500, description="Descripción del video.")
    duration_seconds: int = Field(..., gt=0, description="Duración del video en segundos.")
    rating_stars: int = Field(..., ge=1, le=5, description="Calificación del video de 1 a 5 estrellas.")
    uploader_username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario de quien subió el video.")

# Entity
class VideoInDB(VideoCreate):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id", description="ID único del video en la base de datos (MongoDB ObjectId).")
    video_uuid: UUID = Field(default_factory=uuid4, description="UUID único para identificar el video públicamente.")
    views: int = Field(default=0, ge=0, description="Número de visualizaciones del video.")
    upload_date: datetime = Field(default_factory=datetime.utcnow, description="Fecha y hora de subida del video.")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            UUID: str
        }
        validate_by_name = True

# DTO
class VideoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100, description="Nuevo título del video.")
    description: Optional[str] = Field(None, max_length=500, description="Nueva descripción del video.")
    duration_seconds: Optional[int] = Field(None, gt=0, description="Nueva duración del video en segundos.")
    rating_stars: Optional[int] = Field(None, ge=1, le=5, description="Nueva calificación del video de 1 a 5 estrellas.")
    uploader_username: Optional[str] = Field(None, min_length=3, max_length=50, description="Nuevo nombre de usuario de quien subió el video.")
    views: Optional[int] = Field(None, ge=0, description="Nuevo número de visualizaciones del video.")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            UUID: str
        }