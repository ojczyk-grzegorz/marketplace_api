from fastapi import status, APIRouter
from utils.routers import TimedRoute


router = APIRouter(prefix="/home", tags=["Authentication"], route_class=TimedRoute)

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    description="Health check",
)
async def root():
    return {"message": "Test"}
