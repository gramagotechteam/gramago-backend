# from decimal import Decimal

# from fastapi import (
#     HTTPException,
#     status,
# )
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.commerce_setting import (
#     CommerceSetting,
# )
# from app.repositories.commerce_settings_repository import (
#     CommerceSettingsRepository,
# )


# class CommerceSettingsService:

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):
#         self.db = db

#         self.settings_repository = (
#             CommerceSettingsRepository(
#                 db
#             )
#         )

#     # =========================================================
#     # GET CURRENT SETTINGS
#     # =========================================================

#     async def get_settings(
#         self,
#     ) -> CommerceSetting:

#         settings = (
#             await self.settings_repository
#             .get()
#         )

#         if not settings:

#             # This should never normally happen because
#             # Stage 1 migration inserted id=1.
#             #
#             # We deliberately do NOT silently invent business
#             # settings here because missing commerce config is
#             # a server configuration problem.
#             raise HTTPException(
#                 status_code=(
#                     status.HTTP_500_INTERNAL_SERVER_ERROR
#                 ),
#                 detail=(
#                     "Commerce settings are not configured"
#                 ),
#             )

#         return settings

#     # =========================================================
#     # UPDATE SETTINGS
#     #
#     # Returns:
#     #
#     # (
#     #     updated_settings,
#     #     became_free_delivery,
#     # )
#     #
#     # became_free_delivery is True ONLY when:
#     #
#     # OLD fee > 0
#     # NEW fee == 0
#     #
#     # This is what we will use later for the broadcast.
#     # =========================================================

#     async def update_settings(
#         self,
#         *,
#         minimum_order_amount: Decimal | None,
#         delivery_fee: Decimal | None,
#         updated_by: int,
#     ) -> tuple[
#         CommerceSetting,
#         bool,
#     ]:

#         try:

#             settings = (
#                 await self.settings_repository
#                 .get_for_update()
#             )

#             if not settings:

#                 raise HTTPException(
#                     status_code=(
#                         status.HTTP_500_INTERNAL_SERVER_ERROR
#                     ),
#                     detail=(
#                         "Commerce settings are not configured"
#                     ),
#                 )

#             # -------------------------------------------------
#             # CAPTURE OLD DELIVERY FEE BEFORE UPDATE
#             # -------------------------------------------------

#             old_delivery_fee = Decimal(
#                 settings.delivery_fee
#             )

#             # -------------------------------------------------
#             # MINIMUM ORDER AMOUNT
#             # -------------------------------------------------

#             if minimum_order_amount is not None:

#                 minimum_order_amount = (
#                     self._normalize_money(
#                         minimum_order_amount
#                     )
#                 )

#                 if minimum_order_amount < 0:

#                     raise HTTPException(
#                         status_code=(
#                             status.HTTP_422_UNPROCESSABLE_ENTITY
#                         ),
#                         detail=(
#                             "Minimum order amount "
#                             "cannot be negative"
#                         ),
#                     )

#                 settings.minimum_order_amount = (
#                     minimum_order_amount
#                 )

#             # -------------------------------------------------
#             # DELIVERY FEE
#             # -------------------------------------------------

#             if delivery_fee is not None:

#                 delivery_fee = (
#                     self._normalize_money(
#                         delivery_fee
#                     )
#                 )

#                 if delivery_fee < 0:

#                     raise HTTPException(
#                         status_code=(
#                             status.HTTP_422_UNPROCESSABLE_ENTITY
#                         ),
#                         detail=(
#                             "Delivery fee cannot be negative"
#                         ),
#                     )

#                 settings.delivery_fee = (
#                     delivery_fee
#                 )

#             # -------------------------------------------------
#             # AUDIT
#             # -------------------------------------------------

#             settings.updated_by = (
#                 updated_by
#             )

#             # -------------------------------------------------
#             # TRANSITION DETECTION
#             # -------------------------------------------------

#             new_delivery_fee = Decimal(
#                 settings.delivery_fee
#             )

#             became_free_delivery = (
#                 old_delivery_fee
#                 > Decimal("0.00")
#                 and
#                 new_delivery_fee
#                 == Decimal("0.00")
#             )

#             # -------------------------------------------------
#             # COMMIT
#             # -------------------------------------------------

#             await self.db.commit()

#             await self.db.refresh(
#                 settings
#             )

#             return (
#                 settings,
#                 became_free_delivery,
#             )

#         except HTTPException:

#             await self.db.rollback()

#             raise

#         except Exception:

#             await self.db.rollback()

#             raise

#     # =========================================================
#     # MONEY NORMALIZATION
#     # =========================================================

#     @staticmethod
#     def _normalize_money(
#         value: Decimal,
#     ) -> Decimal:

#         return Decimal(value).quantize(
#             Decimal("0.01")
#         )



import logging
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.commerce_setting import (
    CommerceSetting,
)
from app.repositories.commerce_settings_repository import (
    CommerceSettingsRepository,
)
from app.services.broadcast_notification_service import (
    BroadcastNotificationService,
)


logger = logging.getLogger(
    __name__
)


class CommerceSettingsService:

    MONEY_STEP = Decimal(
        "0.01"
    )

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.settings_repository = (
            CommerceSettingsRepository(
                db
            )
        )

        self.broadcast_service = (
            BroadcastNotificationService(
                db
            )
        )


    # =========================================================
    # GET CURRENT COMMERCE SETTINGS
    # =========================================================

    async def get_settings(
        self,
    ) -> CommerceSetting:

        settings = (
            await self.settings_repository
            .get()
        )

        if not settings:

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Commerce settings are not configured"
                ),
            )

        return settings


    # =========================================================
    # UPDATE SETTINGS
    #
    # Returns:
    #
    # (
    #     settings,
    #     became_free_delivery,
    # )
    #
    # Free-delivery transition:
    #
    # old fee > 0
    # new fee == 0
    #
    # =========================================================

    async def update_settings(
        self,
        *,
        minimum_order_amount: Decimal | None,
        delivery_fee: Decimal | None,
        updated_by: int,
    ) -> tuple[
        CommerceSetting,
        bool,
    ]:

        try:

            # =================================================
            # LOCK SINGLE SETTINGS ROW
            # =================================================

            settings = (
                await self.settings_repository
                .get_for_update()
            )

            if not settings:

                raise HTTPException(
                    status_code=(
                        status.HTTP_500_INTERNAL_SERVER_ERROR
                    ),
                    detail=(
                        "Commerce settings are not configured"
                    ),
                )


            # =================================================
            # SAVE OLD DELIVERY FEE
            #
            # Must be captured BEFORE updating.
            # =================================================

            old_delivery_fee = (
                self._normalize_money(
                    settings.delivery_fee
                )
            )


            # =================================================
            # MINIMUM ORDER AMOUNT
            # =================================================

            if minimum_order_amount is not None:

                normalized_minimum = (
                    self._normalize_money(
                        minimum_order_amount
                    )
                )

                if (
                    normalized_minimum
                    <
                    Decimal("0.00")
                ):

                    raise HTTPException(
                        status_code=(
                            status.HTTP_422_UNPROCESSABLE_ENTITY
                        ),
                        detail=(
                            "Minimum order amount "
                            "cannot be negative"
                        ),
                    )

                settings.minimum_order_amount = (
                    normalized_minimum
                )


            # =================================================
            # DELIVERY FEE
            # =================================================

            if delivery_fee is not None:

                normalized_delivery_fee = (
                    self._normalize_money(
                        delivery_fee
                    )
                )

                if (
                    normalized_delivery_fee
                    <
                    Decimal("0.00")
                ):

                    raise HTTPException(
                        status_code=(
                            status.HTTP_422_UNPROCESSABLE_ENTITY
                        ),
                        detail=(
                            "Delivery fee cannot be negative"
                        ),
                    )

                settings.delivery_fee = (
                    normalized_delivery_fee
                )


            # =================================================
            # AUDIT
            # =================================================

            settings.updated_by = (
                updated_by
            )


            # =================================================
            # DETECT PAID → FREE TRANSITION
            # =================================================

            new_delivery_fee = (
                self._normalize_money(
                    settings.delivery_fee
                )
            )

            became_free_delivery = (
                old_delivery_fee
                >
                Decimal("0.00")
                and
                new_delivery_fee
                ==
                Decimal("0.00")
            )


            # =================================================
            # COMMIT SETTINGS FIRST
            #
            # Important:
            #
            # Notification failure must NOT rollback a valid
            # commerce settings update.
            # =================================================

            await self.db.commit()

            await self.db.refresh(
                settings
            )


        except HTTPException:

            await self.db.rollback()

            raise


        except Exception:

            await self.db.rollback()

            logger.exception(
                "Failed to update commerce settings"
            )

            raise


        # =====================================================
        # BROADCAST AFTER SUCCESSFUL COMMIT
        #
        # Only:
        #
        # positive fee → zero
        #
        # =====================================================

        if became_free_delivery:

            await self._send_free_delivery_broadcast()


        return (
            settings,
            became_free_delivery,
        )


    # =========================================================
    # FREE DELIVERY BROADCAST
    # =========================================================

    async def _send_free_delivery_broadcast(
        self,
    ) -> None:

        try:

            result = (
                await self.broadcast_service
                .send(

                    # -----------------------------------------
                    # TYPE
                    # -----------------------------------------

                    notification_type=(
                        "FREE_DELIVERY"
                    ),

                    # -----------------------------------------
                    # PROMOTIONS
                    #
                    # Your existing broadcast service maps
                    # PROMOTIONS to gramago_offers.
                    # -----------------------------------------

                    category=(
                        "PROMOTIONS"
                    ),

                    # -----------------------------------------
                    # CONTENT
                    # -----------------------------------------

                    title=(
                        "Free Delivery is Live! 🎉"
                    ),

                    message=(
                        "Order your favourites on GramaGo "
                        "now and enjoy free delivery."
                    ),

                    # -----------------------------------------
                    # PUBLIC NAVIGATION
                    #
                    # Works for guest + logged-in users.
                    # -----------------------------------------

                    action=(
                        "OPEN_HOME"
                    ),

                    reference_type=None,

                    reference_id=None,

                    # -----------------------------------------
                    # OPTIONAL METADATA
                    # -----------------------------------------

                    metadata={
                        "delivery_fee": (
                            "0.00"
                        ),

                        "is_free_delivery": (
                            "true"
                        ),
                    },
                )
            )


            # =================================================
            # RESULT LOGGING
            #
            # Do not log FCM tokens.
            # =================================================

            if not result.get(
                "success",
                False,
            ):

                logger.warning(
                    "Free delivery broadcast "
                    "completed without success"
                )

            else:

                logger.info(
                    "Free delivery broadcast "
                    "sent successfully"
                )


        except Exception:

            # =================================================
            # PUSH FAILURE MUST NOT BREAK SETTINGS
            #
            # At this point:
            #
            # commerce settings have already committed.
            #
            # =================================================

            logger.exception(
                "Free delivery broadcast failed"
            )


    # =========================================================
    # MONEY NORMALIZATION
    # =========================================================

    @classmethod
    def _normalize_money(
        cls,
        value,
    ) -> Decimal:

        return Decimal(
            str(value)
        ).quantize(
            cls.MONEY_STEP,
            rounding=ROUND_HALF_UP,
        )