from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import marr_hildreth_routes, canny_routes, otsu_method_routes
import uvicorn
from config import Settings
import os


try:
    settings = Settings()
    settings.validate()
except Exception as e:
    print(f"Configuration Error: {e}")
    exit(1)

if os.getenv("ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv()

app = FastAPI(
    title="filter-applyer-api",
    description="API para aplicar filtros em imagens",
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(marr_hildreth_routes.router)
app.include_router(canny_routes.router)
app.include_router(otsu_method_routes.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Filter Applyer API!",
        "service": "Filter Applyer API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/config")
async def get_config():
    return settings.get_info()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG,
    )