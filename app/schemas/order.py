"""
Schemas for order ingestion endpoint.
"""

from pydantic import BaseModel, Field, RootModel


class RawOrderItem(BaseModel):
    """Single order item in raw order payload."""

    menuItemId: str = Field(..., description="Menu item ID", examples=["M101"])
    quantity: int = Field(..., ge=1, description="Ordered quantity", examples=[2])
    price: float = Field(..., ge=0, description="Unit price", examples=[6])


class RawOrder(BaseModel):
    """Raw order payload item."""

    id: str = Field(..., description="Order ID", examples=["001"])
    restaurantId: str = Field(..., description="Restaurant ID", examples=["R1"])
    items: list[RawOrderItem] = Field(
        ..., description="List of items in the order"
    )


class RawOrderDataRequest(RootModel[list[RawOrder]]):
    """Root payload accepting the same shape as RAW_ORDER_DATA (JSON array)."""


class OrderIngestionData(BaseModel):
    """Response data for order ingestion endpoint."""

    total_received: int = Field(..., description="Total orders received in request")
    inserted_new: int = Field(..., description="New orders inserted")
    replaced_existing: int = Field(..., description="Existing orders replaced")
    restaurants_affected: list[str] = Field(
        ..., description="Restaurant IDs present in payload"
    )


class OrderIngestionResponse(BaseModel):
    """Full response for order ingestion endpoint."""

    success: bool
    data: OrderIngestionData | None = None
    message: str | None = None
