# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.product import Product


# class ProductRepository:

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):
#         self.db = db


#     async def get_by_id(
#         self,
#         product_id: int,
#     ) -> Product | None:

#         result = await self.db.execute(
#             select(Product).where(
#                 Product.id == product_id
#             )
#         )

#         return result.scalar_one_or_none()


#     async def get_by_slug(
#         self,
#         slug: str,
#     ) -> Product | None:

#         result = await self.db.execute(
#             select(Product).where(
#                 Product.slug == slug
#             )
#         )

#         return result.scalar_one_or_none()


#     async def get_active_products(
#         self,
#     ):

#         result = await self.db.execute(
#             select(Product)
#             .where(
#                 Product.is_active.is_(True)
#             )
#             .order_by(
#                 Product.created_at.desc()
#             )
#         )

#         return result.scalars().all()



from sqlalchemy import (
    func,
    or_,
    select,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy.orm import (
    selectinload,
)

from app.models.inventory import Inventory
from app.models.product import Product


class ProductRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    async def get_by_id(
        self,
        product_id: int,
        include_relations: bool = False,
    ) -> Product | None:

        stmt = select(Product).where(
            Product.id == product_id
        )

        if include_relations:

            stmt = stmt.options(
                selectinload(
                    Product.category
                ),
                selectinload(
                    Product.images
                ),
                selectinload(
                    Product.inventory
                ),
            )

        result = await self.db.execute(
            stmt
        )

        return result.scalar_one_or_none()


    async def get_by_slug(
        self,
        slug: str,
    ) -> Product | None:

        result = await self.db.execute(
            select(Product).where(
                Product.slug == slug
            )
        )

        return result.scalar_one_or_none()


    async def search(
        self,
        *,
        search: str | None,
        category_id: int | None,
        featured: bool | None,
        in_stock: bool | None,
        page: int,
        limit: int,
    ):

        conditions = [
            Product.is_active.is_(True)
        ]

        if search:

            keyword = f"%{search.strip()}%"

            conditions.append(
                or_(
                    Product.name.ilike(
                        keyword
                    ),
                    Product.description.ilike(
                        keyword
                    ),
                    Product.sku.ilike(
                        keyword
                    ),
                )
            )

        if category_id is not None:

            conditions.append(
                Product.category_id
                == category_id
            )

        if featured is not None:

            conditions.append(
                Product.is_featured
                == featured
            )

        stmt = select(Product)

        if in_stock is not None:

            stmt = stmt.join(
                Inventory,
                Inventory.product_id
                == Product.id,
            )

            if in_stock:

                conditions.append(
                    (
                        Inventory.available_quantity
                        - Inventory.reserved_quantity
                    ) > 0
                )

            else:

                conditions.append(
                    (
                        Inventory.available_quantity
                        - Inventory.reserved_quantity
                    ) <= 0
                )

        stmt = (
            stmt
            .where(*conditions)
            .options(
                selectinload(
                    Product.category
                ),
                selectinload(
                    Product.images
                ),
                selectinload(
                    Product.inventory
                ),
            )
            .order_by(
                Product.created_at.desc()
            )
        )

        count_stmt = select(
            func.count(Product.id)
        ).where(
            *conditions
        )

        if in_stock is not None:

            count_stmt = (
                select(
                    func.count(Product.id)
                )
                .join(
                    Inventory,
                    Inventory.product_id
                    == Product.id,
                )
                .where(
                    *conditions
                )
            )

        total_result = await self.db.execute(
            count_stmt
        )

        total = total_result.scalar_one()

        offset = (
            page - 1
        ) * limit

        result = await self.db.execute(
            stmt
            .offset(offset)
            .limit(limit)
        )

        products = result.scalars().all()

        return products, total
    
    
    async def admin_list(
    self,
    *,
    search: str | None = None,
    category_id: int | None = None,
    ):

        stmt = (
            select(Product)
            .options(
                selectinload(
                    Product.category
                ),
                selectinload(
                    Product.images
                ),
                selectinload(
                    Product.inventory
                ),
            )
        )

        if search:

            keyword = (
                f"%{search.strip()}%"
            )

            stmt = stmt.where(
                or_(
                    Product.name.ilike(
                        keyword
                    ),
                    Product.sku.ilike(
                        keyword
                    ),
                )
            )

        if category_id:

            stmt = stmt.where(
                Product.category_id
                == category_id
            )

        stmt = stmt.order_by(
            Product.created_at.desc()
        )

        result = await self.db.execute(
            stmt
        )

        return result.scalars().all()