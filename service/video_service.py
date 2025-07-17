import uuid
from typing import List, Optional
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorCollection

from model.video_model import VideoCreate, VideoInDB, VideoUpdate


class VideoService:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create_video(self, video_data: VideoCreate) -> VideoInDB:
        video_dict = video_data.model_dump(by_alias=True)

        if 'video_uuid' not in video_dict:
            video_dict['video_uuid'] = str(uuid.uuid4())

        if 'views' not in video_dict:
            video_dict['views'] = 0

        insert_result = await self.collection.insert_one(video_dict)
        created_video = await self.collection.find_one({'_id': insert_result.inserted_id})

        return VideoInDB(**created_video)

    async def get_all_videos(self, skip: int = 0, limit: int = 100) -> List[VideoInDB]:
        videos_cursor = self.collection.find().skip(skip).limit(limit)
        return [VideoInDB.model_validate(vid) async for vid in videos_cursor]

    async def get_video_by_uuid(self, video_uuid: UUID) -> Optional[VideoInDB]:
        video = await self.collection.find_one({'video_uuid': str(video_uuid)})
        return VideoInDB(**video) if video else None

    async def update_video(self, video_uuid: UUID, video_data: VideoUpdate) -> Optional[VideoInDB]:
        update_data = {k: v for k, v in video_data.model_dump(exclude_unset=True).items()}

        if not update_data:
            return None

        update_result = await self.collection.update_one(
            {'video_uuid': str(video_uuid)},
            {'$set': update_data}
        )
        if update_result.modified_count > 0:
            return await self.get_video_by_uuid(video_uuid)
        return None


    async def delete_video(self, video_uuid: UUID) -> bool:
        delete_result = await self.collection.delete_one({"video_uuid": str(video_uuid)})
        return delete_result.deleted_count == 1


    async def increment_views(self, video_uuid: UUID) -> Optional[VideoInDB]:
        update_result = await self.collection.update_one(
            {"video_uuid": str(video_uuid)},
            {"$inc": {"views": 1}}
        )
        if update_result.modified_count == 1:
            return await self.get_video_by_uuid(video_uuid)
        return None