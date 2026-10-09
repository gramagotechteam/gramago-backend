from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
)


class DeliveryRejectRequest(BaseModel):
    reason: str = Field(
        min_length=3,
        max_length=500,
    )


class DeliveryCompleteRequest(BaseModel):
    otp: str = Field(
        min_length=4,
        max_length=10,
    )

    cod_collected_amount: Decimal | None = Field(
        default=None,
        ge=0,
    )
    
    
    

class DeliveryFailedRequest(BaseModel):
    reason: str = Field(
        min_length=3,
        max_length=500,
    )