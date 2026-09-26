# # from pydantic import (
# #     BaseModel,
# #     Field,
# # )


# # class DeviceTokenRegisterRequest(
# #     BaseModel
# # ):

# #     token: str = Field(
# #         min_length=20,
# #         max_length=512,
# #     )

# #     platform: str = "android"

# #     device_name: str | None = None

# #     app_version: str | None = None


# # class DeviceTokenRemoveRequest(
# #     BaseModel
# # ):

# #     token: str = Field(
# #         min_length=20,
# #         max_length=512,
# #     )


# from pydantic import (
#     BaseModel,
#     Field,
#     field_validator,
# )


# class DeviceTokenRegisterRequest(
#     BaseModel
# ):

#     token: str = Field(
#         min_length=20,
#         max_length=512,
#     )

#     platform: str = "android"

#     device_name: str | None = None

#     app_version: str | None = None


#     @field_validator("token")
#     @classmethod
#     def clean_token(
#         cls,
#         value: str,
#     ) -> str:

#         return value.strip()


# class DeviceTokenRemoveRequest(
#     BaseModel
# ):

#     token: str = Field(
#         min_length=20,
#         max_length=512,
#     )


#     @field_validator("token")
#     @classmethod
#     def clean_token(
#         cls,
#         value: str,
#     ) -> str:

#         return value.strip()




from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class DeviceTokenRegisterRequest(
    BaseModel
):

    token: str = Field(
        min_length=20,
        max_length=512,
    )

    platform: str = "android"

    device_name: str | None = None

    app_version: str | None = None


    @field_validator("token")
    @classmethod
    def clean_token(
        cls,
        value: str,
    ) -> str:

        return value.strip()


class DeviceTokenLinkRequest(
    BaseModel
):

    token: str = Field(
        min_length=20,
        max_length=512,
    )


    @field_validator("token")
    @classmethod
    def clean_token(
        cls,
        value: str,
    ) -> str:

        return value.strip()


class DeviceTokenMarketingRequest(
    BaseModel
):

    token: str = Field(
        min_length=20,
        max_length=512,
    )

    allow_marketing: bool


    @field_validator("token")
    @classmethod
    def clean_token(
        cls,
        value: str,
    ) -> str:

        return value.strip()