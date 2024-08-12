from fastapi import HTTPException
import logging


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        logging.error(f"AppException: {status_code} - {detail}")


class FileValidationError(AppException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=f"File validation error: {detail}")


class AuthenticationError(AppException):
    def __init__(self, detail: str):
        super().__init__(status_code=401, detail=f"Authentication error: {detail}")


class DatabaseError(AppException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Database error: {detail}")


def handle_error(error: Exception):
    if isinstance(error, AppException):
        raise error
    logging.error(f"Unexpected error: {str(error)}")
    raise AppException(status_code=500, detail="An unexpected error occurred")