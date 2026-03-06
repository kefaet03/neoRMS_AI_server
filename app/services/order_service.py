"""
Order ingestion service.
"""

import json
import sqlite3
from pathlib import Path

from ..schemas.order import RawOrder


DB_PATH = Path(__file__).parent.parent.parent / "orders.db"


class OrderService:
    """Service for writing raw order data into SQLite."""

    def __init__(self) -> None:
        self.db_path = DB_PATH

    def _ensure_orders_table(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                restaurant_id TEXT NOT NULL,
                items TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_restaurant_id ON orders(restaurant_id)"
        )
        conn.commit()
        conn.close()

    def ingest_orders(self, orders: list[RawOrder]) -> dict:
        if not orders:
            return {
                "total_received": 0,
                "inserted_new": 0,
                "replaced_existing": 0,
                "restaurants_affected": [],
            }

        self._ensure_orders_table()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        order_ids = [order.id for order in orders]
        placeholders = ",".join("?" for _ in order_ids)
        cursor.execute(
            f"SELECT order_id FROM orders WHERE order_id IN ({placeholders})",
            order_ids,
        )
        existing_order_ids = {row[0] for row in cursor.fetchall()}

        rows = [
            (
                order.id,
                order.restaurantId,
                json.dumps([item.menuItemId for item in order.items]),
            )
            for order in orders
        ]

        cursor.executemany(
            "INSERT OR REPLACE INTO orders (order_id, restaurant_id, items) VALUES (?, ?, ?)",
            rows,
        )
        conn.commit()
        conn.close()

        replaced_existing = len(existing_order_ids)
        total_received = len(orders)
        inserted_new = total_received - replaced_existing
        restaurants_affected = sorted({order.restaurantId for order in orders})

        return {
            "total_received": total_received,
            "inserted_new": inserted_new,
            "replaced_existing": replaced_existing,
            "restaurants_affected": restaurants_affected,
        }


_order_service: OrderService | None = None


def get_order_service() -> OrderService:
    """Get singleton order service instance."""
    global _order_service

    if _order_service is None:
        _order_service = OrderService()

    return _order_service
