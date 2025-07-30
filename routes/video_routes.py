from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from service.video_service import VideoService
from model.video_model import VideoCreate, VideoInDB, VideoUpdate
from config.database import get_database
from typing import List
from uuid import UUID

router = APIRouter()

async def get_video_service():
    db = get_database()
    return VideoService(db["videos"])


@router.post("/",
             summary="Crear un nuevo video",
             response_description="El video creado y sus metadatos.",
             response_model=VideoInDB,
             status_code=status.HTTP_201_CREATED
             )
async def create_video_route(
        video_data: VideoCreate,
        video_service: VideoService = Depends(get_video_service)
):
    """
    Este endpoint permite registrar un nuevo video.
    """
    try:
        print(video_data)
        new_video = await video_service.create_video(video_data)
        return new_video
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear el video: {e}")


@router.get("/",
            summary="Listar todos los videos",
            response_description="Lista de los videos.",
            response_model=List[VideoInDB]
            )
async def get_all_videos_route(
        skip: int = 0, limit: int = 100,
        video_service: VideoService = Depends(get_video_service)
):
    """
    Este endpoint retorna una lista paginada de todos los videos registrados.
    """
    videos = await video_service.get_all_videos(skip=skip, limit=limit)
    return videos


@router.get("/{video_uuid}",
            summary="Obtener un video por UUID",
            response_description="Metadatos del video.",
            response_model=VideoInDB
            )
async def get_video_by_uuid_route(
        video_uuid: UUID,
        video_service: VideoService = Depends(get_video_service)
):
    """
    Este endpoint retorna los datos de un video específico usando su UUID.
    Incrementa el contador de vistas cada vez que se accede.
    """
    video = await video_service.get_video_by_uuid(video_uuid)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video no encontrado.")

    updated_video = await video_service.increment_views(video_uuid)
    if not updated_video:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al incrementar vistas.")

    return updated_video


@router.patch("/{video_uuid}",
              summary="Actualizar un video por UUID",
              response_description="El video actualizado y sus metadatos.",
              response_model=VideoInDB
              )
async def update_video_route(
        video_uuid: UUID,
        video_data: VideoUpdate,
        video_service: VideoService = Depends(get_video_service)
):
    """
    Este endpoint permite actualizar datos de un video usando su UUID.
    """
    updated_video = await video_service.update_video(video_uuid, video_data)
    if not updated_video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Video no encontrado o no hay datos para actualizar.")
    return updated_video


@router.delete("/{video_uuid}",
               summary="Eliminar un video por UUID",
               response_description="Confirmación de eliminación."
               )
async def delete_video_route(
        video_uuid: UUID,
        video_service: VideoService = Depends(get_video_service)
):
    """
    Este endpoint permite eliminar un video de la base de datos usando su UUID.
    """
    deleted = await video_service.delete_video(video_uuid)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video no encontrado.")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Video eliminado exitosamente."})