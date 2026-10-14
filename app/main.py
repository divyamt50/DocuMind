import logging
from fastapi import FastAPI
from app.api.auth import router as auth_router
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.documents import router as documents_router

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(auth_router)
app.include_router(documents_router)

@app.get("/healthz")
def get_status():
    return {"status":"ok"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request:Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "error":{
                "code":"http_error",
                "detail":str(exc.detail)
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request:Request, exc: RequestValidationError):
    details = [
            {
                "field":".".join(str(part) for part in error["loc"]),
                "message": error["msg"]
            }
            for error in exc.errors()
        ]

    return JSONResponse(
        status_code=422,
        content={
            "error":{
                "code": "validation_error",
                "message": "Request validation error",
                "details": details
            }
        }
    )

@app.exception_handler(Exception)
async def unexpected_exception_handler(request:Request, exc:Exception):
        logger.exception("Unhandled application error")

        return JSONResponse(
             status_code=500,
             content={
                  "error":{
                       "code": "internal_server_error",
                       "message": "An unexpected error occured"
                  }
             }
        )