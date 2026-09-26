import asyncio

import cloudinary.uploader
from fastapi import (
    HTTPException,
    UploadFile,
    status,
)

from app.core import cloudinary_config


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


MAX_IMAGE_SIZE = 10 * 1024 * 1024


class CloudinaryService:

    @staticmethod
    async def upload_product_image(
        file: UploadFile,
        product_id: int,
    ) -> dict:

        if file.content_type not in ALLOWED_IMAGE_TYPES:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only JPG, PNG and WEBP "
                    "images are allowed"
                ),
            )

        contents = await file.read()

        if len(contents) > MAX_IMAGE_SIZE:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image size cannot exceed 5 MB",
            )

        try:

            result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                contents,
                folder=(
                    f"gramago/products/"
                    f"{product_id}"
                ),
                resource_type="image",
            )

        except Exception as exc:

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Image upload failed",
            ) from exc

        return {
            "image_url": result["secure_url"],
            "public_id": result["public_id"],
        }


    @staticmethod
    async def delete_image(
        public_id: str,
    ) -> None:

        try:

            await asyncio.to_thread(
                cloudinary.uploader.destroy,
                public_id,
                resource_type="image",
            )

        except Exception:

            pass
        
        
    
    @staticmethod
    async def upload_category_image(
        file: UploadFile,
        category_id: int,
    ) -> dict:

        if file.content_type not in ALLOWED_IMAGE_TYPES:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPG, PNG and WEBP images are allowed",
            )

        contents = await file.read()

        if len(contents) > MAX_IMAGE_SIZE:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image size cannot exceed 5 MB",
            )

        try:

            result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                contents,
                folder=f"gramago/categories/{category_id}",
                resource_type="image",
            )

        except Exception as exc:

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Category image upload failed",
            ) from exc

        return {
            "image_url": result["secure_url"],
            "public_id": result["public_id"],
        }