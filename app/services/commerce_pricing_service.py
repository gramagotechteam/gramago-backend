# from decimal import (
#     Decimal,
#     ROUND_HALF_UP,
# )

# from fastapi import (
#     HTTPException,
#     status,
# )
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.services.commerce_settings_service import (
#     CommerceSettingsService,
# )


# class CommercePricingService:

#     MONEY_STEP = Decimal("0.01")

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):
#         self.db = db

#         self.settings_service = (
#             CommerceSettingsService(
#                 db
#             )
#         )

#     # =========================================================
#     # BUILD CURRENT ORDER PRICING
#     #
#     # subtotal MUST come from backend cart/product calculations.
#     #
#     # Never accept subtotal/delivery fee from Flutter.
#     # =========================================================

#     async def calculate(
#         self,
#         *,
#         subtotal: Decimal,
#         discount: Decimal = Decimal("0.00"),
#     ) -> dict:

#         subtotal = self._money(
#             subtotal
#         )

#         discount = self._money(
#             discount
#         )

#         if subtotal < Decimal("0.00"):
#             raise HTTPException(
#                 status_code=(
#                     status.HTTP_400_BAD_REQUEST
#                 ),
#                 detail="Invalid cart subtotal",
#             )

#         if discount < Decimal("0.00"):
#             raise HTTPException(
#                 status_code=(
#                     status.HTTP_400_BAD_REQUEST
#                 ),
#                 detail="Invalid discount",
#             )

#         settings = (
#             await self.settings_service
#             .get_settings()
#         )

#         minimum_order_amount = self._money(
#             settings.minimum_order_amount
#         )

#         delivery_fee = self._money(
#             settings.delivery_fee
#         )

#         # =====================================================
#         # MINIMUM ORDER VALIDATION
#         # =====================================================

#         if subtotal < minimum_order_amount:

#             amount_remaining = self._money(
#                 minimum_order_amount
#                 - subtotal
#             )

#             raise HTTPException(
#                 status_code=(
#                     status.HTTP_400_BAD_REQUEST
#                 ),
#                 detail=(
#                     "Minimum order amount is "
#                     f"₹{minimum_order_amount:.2f}. "
#                     f"Add ₹{amount_remaining:.2f} "
#                     "more to place your order."
#                 ),
#             )

#         # =====================================================
#         # TOTAL
#         # =====================================================

#         total = self._money(
#             subtotal
#             + delivery_fee
#             - discount
#         )

#         if total < Decimal("0.00"):
#             total = Decimal("0.00")

#         return {
#             "subtotal": subtotal,

#             "minimum_order_amount": (
#                 minimum_order_amount
#             ),

#             "delivery_fee": (
#                 delivery_fee
#             ),

#             "discount": discount,

#             "total": total,

#             "is_free_delivery": (
#                 delivery_fee
#                 == Decimal("0.00")
#             ),
#         }

#     # =========================================================
#     # MONEY NORMALIZATION
#     # =========================================================

#     @classmethod
#     def _money(
#         cls,
#         value,
#     ) -> Decimal:

#         return Decimal(
#             str(value)
#         ).quantize(
#             cls.MONEY_STEP,
#             rounding=ROUND_HALF_UP,
#         )



from decimal import (
    Decimal,
    ROUND_HALF_UP,
)

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.commerce_settings_service import (
    CommerceSettingsService,
)


class CommercePricingService:

    MONEY_STEP = Decimal("0.01")

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.settings_service = (
            CommerceSettingsService(
                db
            )
        )

    # =========================================================
    # CALCULATE CURRENT ORDER PRICING
    #
    # IMPORTANT:
    #
    # subtotal must come from backend product/cart validation.
    #
    # Client must NEVER send:
    # - subtotal
    # - delivery_fee
    # - minimum_order_amount
    # - total
    #
    # =========================================================

    async def calculate(
        self,
        *,
        subtotal: Decimal,
        discount: Decimal = Decimal("0.00"),
    ) -> dict:

        subtotal = self._money(
            subtotal
        )

        discount = self._money(
            discount
        )

        # -----------------------------------------------------
        # BASIC VALIDATION
        # -----------------------------------------------------

        if subtotal < Decimal("0.00"):

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Invalid cart subtotal"
                ),
            )

        if discount < Decimal("0.00"):

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Invalid discount amount"
                ),
            )

        # -----------------------------------------------------
        # CURRENT ADMIN-CONTROLLED SETTINGS
        # -----------------------------------------------------

        settings = (
            await self.settings_service
            .get_settings()
        )

        minimum_order_amount = (
            self._money(
                settings.minimum_order_amount
            )
        )

        delivery_fee = self._money(
            settings.delivery_fee
        )

        # -----------------------------------------------------
        # MINIMUM ORDER AMOUNT
        #
        # This validation is based ONLY on product subtotal.
        # Delivery fee does not help satisfy minimum order.
        # -----------------------------------------------------

        if subtotal < minimum_order_amount:

            amount_remaining = self._money(
                minimum_order_amount
                - subtotal
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    f"Minimum order amount is "
                    f"₹{minimum_order_amount:.2f}. "
                    f"Add ₹{amount_remaining:.2f} "
                    f"more to place your order."
                ),
            )

        # -----------------------------------------------------
        # TOTAL
        # -----------------------------------------------------

        total = self._money(
            subtotal
            + delivery_fee
            - discount
        )

        if total < Decimal("0.00"):

            total = Decimal("0.00")

        return {
            "subtotal": subtotal,

            "minimum_order_amount": (
                minimum_order_amount
            ),

            "delivery_fee": (
                delivery_fee
            ),

            "discount": (
                discount
            ),

            "total": (
                total
            ),

            "is_free_delivery": (
                delivery_fee
                == Decimal("0.00")
            ),
        }

    # =========================================================
    # MONEY NORMALIZER
    # =========================================================

    @classmethod
    def _money(
        cls,
        value,
    ) -> Decimal:

        return Decimal(
            str(value)
        ).quantize(
            cls.MONEY_STEP,
            rounding=ROUND_HALF_UP,
        )