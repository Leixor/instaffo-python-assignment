from fastapi import APIRouter

from api.routes import candidates, jobs

api_router = APIRouter()
api_router.include_router(candidates.router)
api_router.include_router(jobs.router)
