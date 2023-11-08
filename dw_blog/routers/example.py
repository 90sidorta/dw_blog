from fastapi import APIRouter, Depends

from dw_blog.models.example import SongCreate
from dw_blog.services.example import ExampleService, get_example_service

router = APIRouter()

@router.post("/songs")
async def add_song(
    request: SongCreate,
    example_service: ExampleService = Depends(get_example_service),
):
    return await example_service.create(**request.dict())
