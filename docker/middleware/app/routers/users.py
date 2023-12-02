from fastapi import APIRouter

router = APIRouter()


@router.get("/all", tags=["users"])
async def read_users():
    return [{"username": "Test-1"}, {"username": "Test-2"}]
