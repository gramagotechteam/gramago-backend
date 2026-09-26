from fastapi import APIRouter, Depends

from app.dependencies.auth import require_admin
from app.models.user import User


router = APIRouter()


@router.get("/test")
async def admin_test(
    current_user: User = Depends(
        require_admin
    ),
):
    return {
        "success": True,
        "message": "Admin access granted",
        "data": {
            "user_id": current_user.id,
            "role": current_user.role,
        },
    }