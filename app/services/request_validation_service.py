from flask import request, jsonify
from functools import wraps
from app.errors import RequestValidationError
from pydantic import BaseModel, ValidationError
from typing import Type

UNASSIGNED = [...]

def JSONRequestRequired(schema: Type[BaseModel]):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            requestedData = request.get_json()
            if requestedData is not None:
                try:
                    requestedData = schema(**requestedData)
                except ValidationError as exception:
                    # Split exeption string into dictionary elements
                    exceptionString = str(exception).split("\n")
                    descriptions = []
                    for i in range(1, len(exceptionString), 2):
                        fieldName = exceptionString[i]
                        fieldDescription = exceptionString[i + 1][1:]
                        fieldDescription = fieldDescription[:fieldDescription.find(" (")]
                        descriptions.append("".join([fieldName, fieldDescription]))
                    return RequestValidationError(exception=exception).toJSONResponse()
                else:
                    return function(requestedData, *args, **kwargs)
            else:
                return {
                    "error":        "InvalidRequestFormat",
                    "description":  "Request JSON is in invalid format or contains invalid value"
                }, 415
        return wrapper
    return decorator



