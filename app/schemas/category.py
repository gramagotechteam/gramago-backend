from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=120,
    )

    description: str | None = None

    parent_id: int | None = None

    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
    )

    description: str | None = None

    parent_id: int | None = None

    sort_order: int | None = None

    is_active: bool | None = None


class CategoryResponse(BaseModel):
    id: int

    parent_id: int | None

    name: str
    slug: str

    description: str | None

    image_url: str | None

    sort_order: int
    is_active: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )