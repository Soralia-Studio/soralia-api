from fastapi import APIRouter

__all__ = ["router"]

router = APIRouter(prefix="/base", tags=["base"])


@router.get("/")
async def root():
    return "Hello world"
