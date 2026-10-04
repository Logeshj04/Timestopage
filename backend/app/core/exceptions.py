from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "APP_ERROR") -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


def error_body(code: str, message: str, details: list | None = None) -> dict:
    payload: dict = {"error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return payload


def _friendly_validation_message(error: dict) -> str:
    loc = ".".join(str(part) for part in error.get("loc", []) if part != "body")
    msg = error.get("msg", "Invalid value")
    field_messages = {
        "duration_minutes": "Please enter the stoppage duration in minutes.",
        "production_date": "Please select a production date.",
        "shift_id": "Please select a shift.",
        "supervisor_id": "Please select a supervisor.",
        "machine_id": "Please select a machine.",
        "stoppage_reason_id": "Please select a stoppage reason.",
        "username": "Please enter your username.",
        "password": "Please enter your password.",
    }
    for key, text in field_messages.items():
        if key in loc:
            return text
    if "greater than 0" in msg.lower() or "greater_than" in str(error.get("type")):
        return "Duration must be greater than 0 minutes."
    return f"{loc}: {msg}" if loc else msg


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [_friendly_validation_message(err) for err in exc.errors()]
        message = details[0] if details else "Please check the form and try again."
        return JSONResponse(
            status_code=422,
            content=error_body("VALIDATION_ERROR", message, details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else "Request could not be completed."
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body("HTTP_ERROR", message),
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        request.app.logger.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content=error_body(
                "INTERNAL_ERROR",
                "Something went wrong. Please try again or contact an administrator.",
            ),
        )
