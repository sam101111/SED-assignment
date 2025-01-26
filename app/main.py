from fastapi import FastAPI
from app.database import SessionLocal, engine, Base
from app.routers.issues import router as issues_router
from app.routers.users import router as auth_router
from app.routers.pages import router as pages_router
from contextlib import asynccontextmanager


# Creates the database tables and fastAPI instance
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Help desk API",
    description="Having problems ? try submitting a ticket 😊",
)

# Adds the routers to the fastAPI instance
app.include_router(issues_router, prefix="/api/issues", tags=["issues"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(pages_router, tags=["pages"])


# health check route
@app.head("/health")
@app.get("/health")
async def health_check():
    return "ok"
