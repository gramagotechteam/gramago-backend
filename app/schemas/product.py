# # from datetime import datetime
# # from decimal import Decimal

# # from pydantic import (
# #     BaseModel,
# #     ConfigDict,
# #     Field,
# # )


# # class ProductCreate(BaseModel):

# #     category_id: int

# #     name: str = Field(
# #         min_length=2,
# #         max_length=180,
# #     )

# #     sku: str | None = None

# #     description: str | None = None

# #     price: Decimal = Field(
# #         ge=0
# #     )

# #     discount_price: Decimal | None = Field(
# #         default=None,
# #         ge=0,
# #     )

# #     unit: str

# #     unit_value: Decimal = Field(
# #         default=1,
# #         gt=0,
# #     )

# #     min_order_qty: Decimal = Field(
# #         default=1,
# #         gt=0,
# #     )

# #     max_order_qty: Decimal | None = None

# #     is_featured: bool = False


# # class ProductUpdate(BaseModel):

# #     category_id: int | None = None
# #     name: str | None = None

# #     sku: str | None = None

# #     description: str | None = None

# #     price: Decimal | None = Field(
# #         default=None,
# #         ge=0,
# #     )

# #     discount_price: Decimal | None = None

# #     unit: str | None = None

# #     unit_value: Decimal | None = None

# #     min_order_qty: Decimal | None = None

# #     max_order_qty: Decimal | None = None

# #     is_active: bool | None = None
# #     is_featured: bool | None = None


# # class ProductResponse(BaseModel):

# #     id: int

# #     category_id: int

# #     name: str
# #     slug: str

# #     sku: str | None

# #     description: str | None

# #     price: Decimal

# #     discount_price: Decimal | None

# #     unit: str
# #     unit_value: Decimal

# #     min_order_qty: Decimal
# #     max_order_qty: Decimal | None

# #     is_active: bool
# #     is_featured: bool

# #     created_at: datetime

# #     model_config = ConfigDict(
# #         from_attributes=True
# #     )

# from datetime import datetime
# from decimal import Decimal

# from pydantic import (
#     BaseModel,
#     ConfigDict,
#     Field,
# )


# class ProductCreate(BaseModel):
#     category_id: int

#     name: str = Field(
#         min_length=2,
#         max_length=180,
#     )

#     sku: str | None = None
#     description: str | None = None

#     price: Decimal = Field(
#         ge=0
#     )

#     discount_price: Decimal | None = Field(
#         default=None,
#         ge=0,
#     )

#     unit: str

#     unit_value: Decimal = Field(
#         default=1,
#         gt=0,
#     )

#     min_order_qty: Decimal = Field(
#         default=1,
#         gt=0,
#     )

#     max_order_qty: Decimal | None = Field(
#         default=None,
#         gt=0,
#     )

#     is_featured: bool = False


# class ProductUpdate(BaseModel):
#     category_id: int | None = None

#     name: str | None = Field(
#         default=None,
#         min_length=2,
#         max_length=180,
#     )

#     sku: str | None = None
#     description: str | None = None

#     price: Decimal | None = Field(
#         default=None,
#         ge=0,
#     )

#     discount_price: Decimal | None = Field(
#         default=None,
#         ge=0,
#     )

#     unit: str | None = None

#     unit_value: Decimal | None = Field(
#         default=None,
#         gt=0,
#     )

#     min_order_qty: Decimal | None = Field(
#         default=None,
#         gt=0,
#     )

#     max_order_qty: Decimal | None = Field(
#         default=None,
#         gt=0,
#     )

#     is_active: bool | None = None
#     is_featured: bool | None = None


# class CategoryMiniResponse(BaseModel):
#     id: int
#     name: str
#     slug: str

#     model_config = ConfigDict(
#         from_attributes=True
#     )


# class ProductImageResponse(BaseModel):
#     id: int
#     image_url: str
#     alt_text: str | None
#     sort_order: int
#     is_primary: bool

#     model_config = ConfigDict(
#         from_attributes=True
#     )


# class InventoryResponse(BaseModel):
#     available_quantity: Decimal
#     reserved_quantity: Decimal
#     reorder_level: Decimal

#     model_config = ConfigDict(
#         from_attributes=True
#     )


# class ProductResponse(BaseModel):
#     id: int
#     category_id: int

#     name: str
#     slug: str
#     sku: str | None

#     description: str | None

#     price: Decimal
#     discount_price: Decimal | None

#     unit: str
#     unit_value: Decimal

#     min_order_qty: Decimal
#     max_order_qty: Decimal | None

#     is_active: bool
#     is_featured: bool

#     created_at: datetime

#     model_config = ConfigDict(
#         from_attributes=True
#     )


# class ProductDetailResponse(ProductResponse):
#     category: CategoryMiniResponse

#     images: list[ProductImageResponse] = []

#     inventory: InventoryResponse | None = None






















from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
)


class ProductCreate(BaseModel):
    category_id: int

    name: str = Field(
        min_length=2,
        max_length=180,
    )

    sku: str | None = None

    description: str | None = None

    price: Decimal = Field(
        ge=0
    )

    discount_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    unit: str

    unit_value: Decimal = Field(
        default=1,
        gt=0,
    )

    min_order_qty: Decimal = Field(
        default=1,
        gt=0,
    )

    max_order_qty: Decimal | None = Field(
        default=None,
        gt=0,
    )

    is_featured: bool = False


class ProductUpdate(BaseModel):
    category_id: int | None = None

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=180,
    )

    sku: str | None = None

    description: str | None = None

    price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    discount_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    unit: str | None = None

    unit_value: Decimal | None = Field(
        default=None,
        gt=0,
    )

    min_order_qty: Decimal | None = Field(
        default=None,
        gt=0,
    )

    max_order_qty: Decimal | None = Field(
        default=None,
        gt=0,
    )

    is_active: bool | None = None

    is_featured: bool | None = None


class CategoryMiniResponse(BaseModel):
    id: int
    name: str
    slug: str

    model_config = ConfigDict(
        from_attributes=True
    )


class ProductImageResponse(BaseModel):
    id: int

    image_url: str

    alt_text: str | None

    sort_order: int

    is_primary: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# INVENTORY RESPONSE
# ============================================================

class InventoryResponse(BaseModel):
    available_quantity: Decimal

    reserved_quantity: Decimal

    reorder_level: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )


    @computed_field
    @property
    def sellable_quantity(
        self,
    ) -> Decimal:

        sellable = (
            self.available_quantity
            - self.reserved_quantity
        )

        # Safety:
        # never expose negative sellable stock.
        return max(
            sellable,
            Decimal("0"),
        )


# ============================================================
# PRODUCT RESPONSE
# ============================================================

class ProductResponse(BaseModel):
    id: int

    category_id: int

    name: str

    slug: str

    sku: str | None

    description: str | None

    price: Decimal

    discount_price: Decimal | None

    unit: str

    unit_value: Decimal

    min_order_qty: Decimal

    max_order_qty: Decimal | None

    is_active: bool

    is_featured: bool

    created_at: datetime


    # IMPORTANT:
    # Product lists also need stock information.
    inventory: InventoryResponse | None = None


    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# PRODUCT DETAIL RESPONSE
# ============================================================

class ProductDetailResponse(
    ProductResponse
):
    category: CategoryMiniResponse

    images: list[
        ProductImageResponse
    ] = []