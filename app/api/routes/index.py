from fastapi import APIRouter


router = APIRouter()

@router.get("/", name='index')
def index():
    return {"message": "FastAPI ML service is running"}
