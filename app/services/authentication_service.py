from sqlalchemy import *
from sqlalchemy.orm import *
from datetime import datetime, timedelta
from flask import request, jsonify, redirect, url_for, Response
from flask import g as requestContext
from flask import session as clientSession
from typing import Dict
from app.config import Config
from app.data import getDatabaseSession
from app.models.user import User
from app.models.user_api_key import UserApiKey
from app.models.user_session import UserSession
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_permission import UserPermission
from app.models.permission import Permission
from app.models.activity import Activity
from app.extensions.date_time import Time
from app.errors import AuthenticationError
from functools import wraps
import jwt
from typing import Dict, Callable
import time

def authenticationRequired(function: Callable[..., Response]) -> None:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Callable[..., Response]:
        session = getDatabaseSession()
        if request.headers.get("Authorization") is not None:
            requestedString = request.headers["Authorization"]
            bearerPrefix = "Bearer "
            apiKeyPrefix = "APIKey "
            # Login by JWT Token
            if requestedString.find(bearerPrefix) == 0 and len(requestedString) > len(bearerPrefix):
                jwtToken  = requestedString[len(bearerPrefix):]
                secretKey = Config.SECRET_KEY
                try:
                    jwtDecoded: Dict[str, str] = jwt.decode(jwtToken, key=secretKey, algorithms="HS256")
                    expirationTime = datetime.fromisoformat(jwtDecoded.get("expiration"))
                    if expirationTime < Time.getCurrentDateTime():
                        raise AuthenticationError("JWT Token has expired")
                    user = session.scalars(
                        select(User)
                        .where(User.id == jwtDecoded.get("userID"))
                    ).first()
                    if user is None or user.userName != jwtDecoded.get("userName"):
                        raise AuthenticationError("JWT Token is invalid")
                    requestContext.requestedUser = user
                    return function(*args, **kwargs)
                except AuthenticationError as exception:
                    response = jsonify({
                        "error": type(exception).__name__,
                        "description": "JWT Token has expired"})
                    response.status_code = 401
                    return response
            # Login by API Key
            elif requestedString.find(apiKeyPrefix) == 0 and len(requestedString) > len(apiKeyPrefix):
                requestedApiKey = requestedString[len(apiKeyPrefix):]
                userApiKey: UserApiKey = (
                    session.query(UserApiKey)
                    .filter(UserApiKey.key==requestedApiKey)
                    .first())
                if userApiKey is not None:
                    user = userApiKey.user
                    invalidKey = (userApiKey.key != requestedApiKey)
                    expiredKey = userApiKey.expiringDateTime < Time.getCurrentDateTime()
                    if not invalidKey and not expiredKey:
                        userApiKey.lastUsedDateTime = Time.getCurrentDateTime()
                        userApiKey.lastUsedIPAddress = request.remote_addr
                        userApiKey.userAgent = request.headers.get("User-Agent")
                        session.commit()
                        requestContext.requestedUser = user
                        return function(*args, **kwargs)
                    # Response error when key is invalid
                    return jsonify({
                        "error":        "AuthenticationError",
                        "description":  "API key is not valid"
                    }), 401
                # Response error when user with given ID doesn't exist
                return {
                    "error":        "AuthenticationError",
                    "description":  "User doesn't exist"
                }, 401
            return {
                "error": "AuthenticationError",
                "description": "Request is cannot be authenticated"
            }, 401
    return wrapper

def loginRequired(function: Callable[..., Response]) -> Response:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any):
        session = getDatabaseSession()
        # Validate user identity and session token in client's session
        try:
            userID: int | None = clientSession.get("userID")
            sessionToken: str | None = clientSession.get("sessionToken")
        except TypeError:
            clientSession["beforeLoginURL"] = request.url
            return redirect(url_for("login"))
        
        # Check if user has logged in
        if userID is None or sessionToken is None:
            return redirect(url_for("login"))
        user = session.scalars(
            select(User)
            .join(User.session)
            .options(
                joinedload(User.userPermissions).joinedload(UserPermission.permission),
                joinedload(User.roles).joinedload(Role.rolePermissions).joinedload(RolePermission.permission),
                joinedload(User.photos)
            ).where(
                and_(
                    User.id == userID,
                    UserSession.token == sessionToken
                )
            )
        ).unique().first()
        requestContext.requestedUser = user
        if user is None:
            clientSession.pop("userID")
            clientSession.pop("sessionToken")
            clientSession["beforeLoginURL"] = request.url
            return redirect(url_for("login"))
        
        # User has logged in, update session data in the database
        user.session.refreshSession()
        session.commit()
        return function(*args, **kwargs)
    return wrapper

class AuthenticationService:
    @classmethod
    def getApiKey(cls, userName: str, password: str, ipAddress: str) -> Dict[str, str]:
        session = getDatabaseSession()
        user = session.scalars(
            select(User)
            .where(User.userName == userName)
        ).first()
        if user is not None:
            isPasswordCorrect = user.verifyPassword(password)
            if isPasswordCorrect:
                userApiKey = user.apiKey
                userApiKey.lastUsedDateTime = Time.getCurrentDateTime()
                userApiKey.lastUsedIPAddress = ipAddress
                authenticationData = {
                    "userID":       user.id,
                    "apiKey":       userApiKey.key
                }
                # Logging login action into database
                activity = Activity()
                activity.userID = user.id
                activity.action = Activity.Actions.GettingApiKey
                activity.isFinished = True
                session.add(activity)
                session.commit()
                return authenticationData
            else:
                raise AuthenticationError("User's password is incorrect")
        else:
            raise AuthenticationError("User doesn't exist")

    @classmethod
    def getJwtToken(cls, userName: str, password: str) -> str:
        session = getDatabaseSession()
        user = session.scalars(
            select(User)
            .where(User.userName == userName)
        ).first()
        if user is None:
            raise AuthenticationError("Username doesn't exist")
        if not user.verifyPassword(password=password):
            raise AuthenticationError("Password is incorrect")
        payload = {
            "issuer":           user.id,
            "subject":          user.userName,
            "expiration":       Time.getCurrentDateTime() + timedelta(hours=2)
        }
        secretKey = Config.SECRET_KEY
        algorithm = "HS256"
        jwtToken = jwt.encode(payload=payload, key=secretKey, algorithm=algorithm)
        return jwtToken

    @classmethod
    def login(cls, userName: str, password: str) -> Dict[str, Any]:
        session = getDatabaseSession()
        user = session.scalars(
            select(User)
            .options(joinedload(User.session))
            .where(User.userName == userName)
        ).first()
        # Checking if staff username is existing in the database
        if user is not None:
            # Checking if password is valid
            if not user.verifyPassword(password):
                raise AuthenticationError("Mật khẩu không đúng.")
            # Login data is valid, modifying session if existing
            if user.session is not None:
                user.session.generateNewSessionToken(
                    ipAddress=request.remote_addr,
                    userAgent=request.user_agent.string)
            # Create new session if user has no session
            else:
                userSession = UserSession(
                    userID=user.id,
                    ipAddress=request.remote_addr,
                    userAgent=request.user_agent.string)
                user.session = userSession
            session.commit()
            return {
                "userID":           user.id,
                "sessionToken":     user.session.token
            }
        else:
            raise AuthenticationError("Tài khoản không tồn tại.")
        
    @classmethod
    @authenticationRequired
    def logout(cls) -> None:
        session = getDatabaseSession()
        requestedUser: User = requestContext.requestedUser
        requestedSession: UserSession = requestedUser.session
        session.delete(requestedSession)
        session.commit()