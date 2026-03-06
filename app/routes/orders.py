"""
Order ingestion endpoint.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from ..schemas.order import (
    OrderIngestionData,
    OrderIngestionResponse,
    RawOrderDataRequest,
)
from ..services.order_service import get_order_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "/import",
    response_model=OrderIngestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Import Raw Orders",
    description="""
    Insert or update order data in the same shape as RAW_ORDER_DATA.

    Expects a JSON array where each item has:
    - id
    - restaurantId
    - items: [{menuItemId, quantity, price}]

    Stored DB format keeps only menuItemId list for recommendation use.
    """,
)
async def import_orders(request: RawOrderDataRequest) -> OrderIngestionResponse:
    """Import raw orders into SQLite orders table."""
    try:
        service = get_order_service()
        result = service.ingest_orders(request.root)

        logger.info(
            "Imported %s orders (%s new, %s replaced)",
            result["total_received"],
            result["inserted_new"],
            result["replaced_existing"],
        )

        return OrderIngestionResponse(
            success=True,
            data=OrderIngestionData(**result),
            message=(
                f"Imported {result['total_received']} orders "
                f"({result['inserted_new']} new, {result['replaced_existing']} replaced)"
            ),
        )
    except Exception as exc:
        logger.error("Order import failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import orders: {str(exc)}",
        )
