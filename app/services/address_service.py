from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_address import (
    UserAddress,
)
from app.repositories.address_repository import (
    AddressRepository,
)
from app.schemas.address import (
    AddressCreate,
    AddressUpdate,
)


class AddressService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db
        self.addresses = AddressRepository(db)


    async def create(
        self,
        user_id: int,
        data: AddressCreate,
    ) -> UserAddress:

        existing = (
            await self.addresses.list_for_user(
                user_id
            )
        )

        make_default = (
            data.is_default
            or len(existing) == 0
        )

        if make_default:

            await self.addresses.clear_default(
                user_id
            )

        address = UserAddress(
            user_id=user_id,
            label=data.label,
            full_name=data.full_name.strip(),
            phone=data.phone.strip(),

            house_no=data.house_no,
            street=data.street,

            village_town=(
                data.village_town.strip()
            ),

            mandal=data.mandal,
            district=data.district.strip(),
            state=data.state.strip(),
            pincode=data.pincode.strip(),

            landmark=data.landmark,

            latitude=data.latitude,
            longitude=data.longitude,

            is_default=make_default,
        )

        self.db.add(address)

        await self.db.commit()
        await self.db.refresh(address)

        return address


    async def update(
        self,
        user_id: int,
        address_id: int,
        data: AddressUpdate,
    ) -> UserAddress:

        address = (
            await self.addresses.get_user_address(
                address_id,
                user_id,
            )
        )

        if not address:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if update_data.get(
            "is_default"
        ) is True:

            await self.addresses.clear_default(
                user_id
            )

        for key, value in update_data.items():

            if key == "is_default":
                continue

            setattr(
                address,
                key,
                value,
            )

        if "is_default" in update_data:

            address.is_default = (
                update_data["is_default"]
            )

        await self.db.commit()
        await self.db.refresh(address)

        return address


    async def set_default(
        self,
        user_id: int,
        address_id: int,
    ) -> UserAddress:

        address = (
            await self.addresses.get_user_address(
                address_id,
                user_id,
            )
        )

        if not address:

            raise HTTPException(
                status_code=404,
                detail="Address not found",
            )

        await self.addresses.clear_default(
            user_id
        )

        address.is_default = True

        await self.db.commit()
        await self.db.refresh(address)

        return address


    async def deactivate(
        self,
        user_id: int,
        address_id: int,
    ) -> None:

        address = (
            await self.addresses.get_user_address(
                address_id,
                user_id,
            )
        )

        if not address:

            raise HTTPException(
                status_code=404,
                detail="Address not found",
            )

        was_default = address.is_default

        address.is_active = False
        address.is_default = False

        await self.db.flush()

        if was_default:

            remaining = (
                await self.addresses.list_for_user(
                    user_id
                )
            )

            for item in remaining:

                if item.id != address.id:

                    item.is_default = True
                    break

        await self.db.commit()