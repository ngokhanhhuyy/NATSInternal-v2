from sqlalchemy import *
from flask import *
from app import application
from app.extensions.date_time import Time
from app.services.authentication_service import loginRequired
from app.services.photo_service import PhotoService
from app.errors import NotFoundError
from base64 import b64encode
from typing import Dict

@application.route("/photos", endpoint="photos", methods=["GET"])
@loginRequired
def photoListPage():
    photos = PhotoService.getAllPhotos()
    return render_template("photo_list.html", photos=photos)

@application.route("/photo/<int:photoID>", endpoint="photo", methods=["GET"])
@loginRequired
def photoPage(photoID: int):
    try:
        photo = PhotoService.getPhotoByID(photoID)
        return render_template("photo.html", photo=photo[photoID])
    except NotFoundError:
        abort(404)


