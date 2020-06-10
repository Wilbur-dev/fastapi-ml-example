from fastapi import APIRouter


router = APIRouter()

@router.get("/", name='index')
def index():
    return {'Welcome'}
