import fastapi
import uvicorn


def initialize_application() -> fastapi.FastAPI:
    app = fastapi.FastAPI()
    return app


app: fastapi.FastAPI = initialize_application()

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4,
    )
