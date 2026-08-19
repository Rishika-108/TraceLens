from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def investigate():
    return {
        "message": "Not implemented"
    }