from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.services.push_notification_service import (
    PushNotificationService,
)


class BroadcastNotificationService:

    def __init__(
        self,
        db: AsyncSession,
    ):

        self.db = db

        self.push = (
            PushNotificationService(
                db
            )
        )


    # async def send(
    #     self,
    #     *,
    #     notification_type: str,
    #     title: str,
    #     message: str,
    #     category: str,
    #     action: str = "OPEN_HOME",
    #     reference_type: str | None = None,
    #     reference_id: int | None = None,
    #     image_url: str | None = None,
    #     metadata: dict | None = None,
    # ) -> dict:

    #     data = {

    #         "type":
    #             notification_type,

    #         "category":
    #             category,

    #         "action":
    #             action,

    #         "reference_type":
    #             reference_type,

    #         "reference_id":
    #             reference_id,
    #     }


    #     if metadata:

    #         data.update(
    #             metadata
    #         )


    #     channel_id = (
    #         self._channel_for_category(
    #             category
    #         )
    #     )
    async def send(
        self,
        *,
        notification_type: str,
        title: str,
        message: str,
        category: str,
        action: str = "OPEN_HOME",
        reference_type: str | None = None,
        reference_id: int | None = None,
        image_url: str | None = None,
        metadata: dict | None = None,
    ) -> dict:

        data = {

            "type":
                notification_type,

            "category":
                category,

            "action":
                action,

            "reference_type":
                reference_type,

            "reference_id":
                reference_id,
        }


        # ----------------------------------------------------------
        # Product image for Flutter foreground notification
        # ----------------------------------------------------------

        if image_url:

            data["image_url"] = (
                image_url
            )


        if metadata:

            data.update(
                metadata
            )


        channel_id = (
            self._channel_for_category(
                category
            )
        )


        return await self.push.send_public(

            title=title,

            body=message,

            data=data,

            # Used by Firebase / Android when app
            # is backgrounded or terminated.
            image_url=image_url,

            channel_id=channel_id,
        )


        # return await self.push.send_public(

        #     title=title,

        #     body=message,

        #     data=data,

        #     image_url=image_url,

        #     channel_id=channel_id,
        # )


    def _channel_for_category(
        self,
        category: str,
    ) -> str:

        if category == "PRODUCTS":

            return "gramago_products"


        if category in {
            "PRICE_ALERTS",
            "PROMOTIONS",
        }:

            return "gramago_offers"


        return "gramago_general"