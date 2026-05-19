from fastapi import HTTPException, status


class InvalidRequest(HTTPException):
    def __init__(
        self,
        message: str = "Invalid Request",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(status_code, detail=message)


class ResourceExists(HTTPException):
    def __init__(
        self,
        message: str = "Resource already exists",
        status_code: int = status.HTTP_409_CONFLICT,
    ):
        super().__init__(status_code, detail=message)


class MissingResource(HTTPException):
    def __init__(
        self,
        message: str = "Resource not found",
        status_code: int = status.HTTP_404_NOT_FOUND,
    ):
        super().__init__(status_code, detail=message)
