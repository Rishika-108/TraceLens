from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def semantic_search():
    return {
        "message": "Not implemented"
    }