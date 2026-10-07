from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.routers.auth import router as auth_router
from src.routers.tasks import router as tasks_router

app = FastAPI(title="Task Manager API")

app.include_router(auth_router)
app.include_router(tasks_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []

    for error in exc.errors():
        message = error["msg"]

        if message.startswith("Value error, "):
            message = message.removeprefix("Value error, ")

        errors.append(message)

    return JSONResponse(status_code=422, content={"detail": errors})


@app.get("/")
def root():
    return {"message": "Task Manager API is running"}
