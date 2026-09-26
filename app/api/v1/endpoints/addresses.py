from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import (
    get_current_user,
)
from app.models.user import User
from app.repositories.address_repository import (
    AddressRepository,
)
from app.schemas.address import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
)
from app.services.address_service import (
    AddressService,
)


router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_address(
    data: AddressCreate,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = AddressService(db)

    address = await service.create(
        current_user.id,
        data,
    )

    return {
        "success": True,
        "message": "Address created successfully",
        "data": AddressResponse.model_validate(
            address
        ),
    }


@router.get("")
async def list_addresses(
    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = AddressRepository(db)

    addresses = await repository.list_for_user(
        current_user.id
    )

    return {
        "success": True,
        "message": "Addresses fetched successfully",
        "data": [
            AddressResponse.model_validate(
                address
            )
            for address in addresses
        ],
    }


@router.patch("/{address_id}")
async def update_address(
    address_id: int,
    data: AddressUpdate,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = AddressService(db)

    address = await service.update(
        current_user.id,
        address_id,
        data,
    )

    return {
        "success": True,
        "message": "Address updated successfully",
        "data": AddressResponse.model_validate(
            address
        ),
    }


@router.post("/{address_id}/default")
async def set_default_address(
    address_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = AddressService(db)

    address = await service.set_default(
        current_user.id,
        address_id,
    )

    return {
        "success": True,
        "message": "Default address updated",
        "data": AddressResponse.model_validate(
            address
        ),
    }


@router.delete("/{address_id}")
async def delete_address(
    address_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = AddressService(db)

    await service.deactivate(
        current_user.id,
        address_id,
    )

    return {
        "success": True,
        "message": "Address removed successfully",
        "data": None,
    }