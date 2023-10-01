from sqlalchemy import *
from sqlalchemy.orm import *
from app.data import getDatabaseSession
from app.models.photo import Photo
from app.errors import NotFoundError
from typing import Dict, List

class PhotoService:
    @classmethod
    def dictionarySerializing(cls, photos: List[Photo]) -> Dict[int, Dict[str, Any]]:
        photosData: Dict[int, Dict[str, str]] = {}
        if len(list(photos)) == 0:
            return photosData
        for photo in photos:
            photosData[photo.id] = {
                "content":              photo.contentDecoded,
                "isPrimary":            photo.isPrimary,
            }
        return photosData
    
    @classmethod
    def getAllPhotos(cls) -> Dict[int, Dict[str, Any]]:
        session = getDatabaseSession()
        photos = session.scalars(
            select(Photo)
            .order_by(Photo.id)
        ).all()
        return cls.dictionarySerializing(photos)
        
    @classmethod
    def getPhotoByID(cls, id: int) -> Dict[int, Dict[str, str]]:
        session = getDatabaseSession()
        photo = session.scalars(
            select(Photo)
            .where(Photo.id == id)
        ).first()
        if photo is None:
            raise NotFoundError(
                modelName="photo",
                id=id)
        return cls.dictionarySerializing([photo])