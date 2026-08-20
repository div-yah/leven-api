from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, categories, ideas, tags, comments, shares, upload

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(ideas.router, prefix="/ideas", tags=["ideas"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(comments.router, prefix="", tags=["comments"])
api_router.include_router(shares.router, prefix="/shares", tags=["shares"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
