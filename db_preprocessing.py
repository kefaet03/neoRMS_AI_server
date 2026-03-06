"""
Database Preprocessing Script.

Pre-processes raw order data and saves it to SQLite database.
This script should be run once to initialize the database with order history.
"""

import sqlite3
import json
from pathlib import Path

# Path to SQLite database
DB_PATH = Path(__file__).parent / "orders.db"

# Raw order data from backend (hardcoded for demonstration)
RAW_ORDER_DATA = [
    {"id": "001", "restaurantId": "R1", "items": [{"menuItemId": "M101", "quantity": 2, "price": 6}, {"menuItemId": "M104", "quantity": 1, "price": 8}]},
    {"id": "002", "restaurantId": "R1", "items": [{"menuItemId": "M102", "quantity": 1, "price": 5}, {"menuItemId": "M106", "quantity": 2, "price": 7}]},
    {"id": "003", "restaurantId": "R1", "items": [{"menuItemId": "M101", "quantity": 1, "price": 6}, {"menuItemId": "M103", "quantity": 1, "price": 9}, {"menuItemId": "M107", "quantity": 2, "price": 4}]},
    {"id": "004", "restaurantId": "R1", "items": [{"menuItemId": "M108", "quantity": 2, "price": 3}, {"menuItemId": "M104", "quantity": 1, "price": 8}]},
    {"id": "005", "restaurantId": "R1", "items": [{"menuItemId": "M105", "quantity": 1, "price": 10}, {"menuItemId": "M106", "quantity": 1, "price": 7}]},
    {"id": "006", "restaurantId": "R1", "items": [{"menuItemId": "M101", "quantity": 3, "price": 6}]},
    {"id": "007", "restaurantId": "R1", "items": [{"menuItemId": "M103", "quantity": 2, "price": 9}, {"menuItemId": "M107", "quantity": 1, "price": 4}]},
    {"id": "008", "restaurantId": "R1", "items": [{"menuItemId": "M108", "quantity": 2, "price": 3}, {"menuItemId": "M102", "quantity": 1, "price": 5}]},
    {"id": "009", "restaurantId": "R1", "items": [{"menuItemId": "M105", "quantity": 1, "price": 10}, {"menuItemId": "M101", "quantity": 1, "price": 6}]},
    {"id": "010", "restaurantId": "R1", "items": [{"menuItemId": "M106", "quantity": 2, "price": 7}, {"menuItemId": "M104", "quantity": 1, "price": 8}]},

    {"id": "011", "restaurantId": "R2", "items": [{"menuItemId": "M201", "quantity": 1, "price": 12}, {"menuItemId": "M205", "quantity": 1, "price": 6}]},
    {"id": "012", "restaurantId": "R2", "items": [{"menuItemId": "M202", "quantity": 2, "price": 5}, {"menuItemId": "M203", "quantity": 1, "price": 8}]},
    {"id": "013", "restaurantId": "R2", "items": [{"menuItemId": "M204", "quantity": 1, "price": 7}, {"menuItemId": "M208", "quantity": 2, "price": 4}]},
    {"id": "014", "restaurantId": "R2", "items": [{"menuItemId": "M206", "quantity": 1, "price": 6}, {"menuItemId": "M201", "quantity": 1, "price": 12}]},
    {"id": "015", "restaurantId": "R2", "items": [{"menuItemId": "M207", "quantity": 3, "price": 3}]},
    {"id": "016", "restaurantId": "R2", "items": [{"menuItemId": "M203", "quantity": 2, "price": 8}, {"menuItemId": "M202", "quantity": 1, "price": 5}]},
    {"id": "017", "restaurantId": "R2", "items": [{"menuItemId": "M204", "quantity": 1, "price": 7}, {"menuItemId": "M205", "quantity": 2, "price": 6}]},
    {"id": "018", "restaurantId": "R2", "items": [{"menuItemId": "M208", "quantity": 1, "price": 4}, {"menuItemId": "M201", "quantity": 1, "price": 12}]},
    {"id": "019", "restaurantId": "R2", "items": [{"menuItemId": "M206", "quantity": 2, "price": 6}, {"menuItemId": "M207", "quantity": 1, "price": 3}]},
    {"id": "020", "restaurantId": "R2", "items": [{"menuItemId": "M202", "quantity": 1, "price": 5}, {"menuItemId": "M203", "quantity": 1, "price": 8}]},

    {"id": "021", "restaurantId": "R3", "items": [{"menuItemId": "M301", "quantity": 2, "price": 9}, {"menuItemId": "M304", "quantity": 1, "price": 7}]},
    {"id": "022", "restaurantId": "R3", "items": [{"menuItemId": "M302", "quantity": 1, "price": 5}, {"menuItemId": "M305", "quantity": 1, "price": 11}]},
    {"id": "023", "restaurantId": "R3", "items": [{"menuItemId": "M303", "quantity": 2, "price": 6}]},
    {"id": "024", "restaurantId": "R3", "items": [{"menuItemId": "M306", "quantity": 1, "price": 10}, {"menuItemId": "M301", "quantity": 1, "price": 9}]},
    {"id": "025", "restaurantId": "R3", "items": [{"menuItemId": "M307", "quantity": 3, "price": 4}]},
    {"id": "026", "restaurantId": "R3", "items": [{"menuItemId": "M308", "quantity": 1, "price": 3}, {"menuItemId": "M304", "quantity": 2, "price": 7}]},
    {"id": "027", "restaurantId": "R3", "items": [{"menuItemId": "M305", "quantity": 1, "price": 11}, {"menuItemId": "M302", "quantity": 2, "price": 5}]},
    {"id": "028", "restaurantId": "R3", "items": [{"menuItemId": "M306", "quantity": 1, "price": 10}, {"menuItemId": "M303", "quantity": 1, "price": 6}]},
    {"id": "029", "restaurantId": "R3", "items": [{"menuItemId": "M307", "quantity": 1, "price": 4}, {"menuItemId": "M301", "quantity": 1, "price": 9}]},
    {"id": "030", "restaurantId": "R3", "items": [{"menuItemId": "M308", "quantity": 2, "price": 3}, {"menuItemId": "M302", "quantity": 1, "price": 5}]},

    {"id": "031", "restaurantId": "R4", "items": [{"menuItemId": "M401", "quantity": 1, "price": 10}, {"menuItemId": "M405", "quantity": 2, "price": 6}]},
    {"id": "032", "restaurantId": "R4", "items": [{"menuItemId": "M402", "quantity": 2, "price": 5}]},
    {"id": "033", "restaurantId": "R4", "items": [{"menuItemId": "M403", "quantity": 1, "price": 7}, {"menuItemId": "M406", "quantity": 1, "price": 8}]},
    {"id": "034", "restaurantId": "R4", "items": [{"menuItemId": "M404", "quantity": 2, "price": 6}, {"menuItemId": "M408", "quantity": 1, "price": 4}]},
    {"id": "035", "restaurantId": "R4", "items": [{"menuItemId": "M407", "quantity": 3, "price": 3}]},
    {"id": "036", "restaurantId": "R4", "items": [{"menuItemId": "M401", "quantity": 1, "price": 10}, {"menuItemId": "M403", "quantity": 1, "price": 7}]},
    {"id": "037", "restaurantId": "R4", "items": [{"menuItemId": "M405", "quantity": 1, "price": 6}, {"menuItemId": "M406", "quantity": 2, "price": 8}]},
    {"id": "038", "restaurantId": "R4", "items": [{"menuItemId": "M408", "quantity": 2, "price": 4}]},
    {"id": "039", "restaurantId": "R4", "items": [{"menuItemId": "M404", "quantity": 1, "price": 6}, {"menuItemId": "M407", "quantity": 1, "price": 3}]},
    {"id": "040", "restaurantId": "R4", "items": [{"menuItemId": "M402", "quantity": 1, "price": 5}, {"menuItemId": "M406", "quantity": 1, "price": 8}]},

    {"id": "041", "restaurantId": "R5", "items": [{"menuItemId": "M501", "quantity": 2, "price": 9}, {"menuItemId": "M505", "quantity": 1, "price": 7}]},
    {"id": "042", "restaurantId": "R5", "items": [{"menuItemId": "M502", "quantity": 1, "price": 5}, {"menuItemId": "M504", "quantity": 1, "price": 6}]},
    {"id": "043", "restaurantId": "R5", "items": [{"menuItemId": "M503", "quantity": 2, "price": 8}]},
    {"id": "044", "restaurantId": "R5", "items": [{"menuItemId": "M506", "quantity": 1, "price": 11}, {"menuItemId": "M501", "quantity": 1, "price": 9}]},
    {"id": "045", "restaurantId": "R5", "items": [{"menuItemId": "M507", "quantity": 3, "price": 4}]},
    {"id": "046", "restaurantId": "R5", "items": [{"menuItemId": "M508", "quantity": 1, "price": 3}, {"menuItemId": "M504", "quantity": 2, "price": 6}]},
    {"id": "047", "restaurantId": "R5", "items": [{"menuItemId": "M505", "quantity": 1, "price": 7}, {"menuItemId": "M502", "quantity": 1, "price": 5}]},
    {"id": "048", "restaurantId": "R5", "items": [{"menuItemId": "M503", "quantity": 1, "price": 8}, {"menuItemId": "M506", "quantity": 1, "price": 11}]},
    {"id": "049", "restaurantId": "R5", "items": [{"menuItemId": "M507", "quantity": 1, "price": 4}, {"menuItemId": "M501", "quantity": 1, "price": 9}]},
    {"id": "050", "restaurantId": "R5", "items": [{"menuItemId": "M508", "quantity": 2, "price": 3}, {"menuItemId": "M502", "quantity": 1, "price": 5}]},
]


def create_database():
    """Create the orders table in SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing table if exists
    cursor.execute("DROP TABLE IF EXISTS orders")
    
    # Create orders table
    # items is stored as JSON string containing list of menuItemIds
    cursor.execute("""
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            restaurant_id TEXT NOT NULL,
            items TEXT NOT NULL
        )
    """)
    
    # Create index on restaurant_id for faster queries
    cursor.execute("CREATE INDEX idx_restaurant_id ON orders(restaurant_id)")
    
    conn.commit()
    conn.close()
    print(f"✓ Database created at: {DB_PATH}")


def preprocess_and_insert_data():
    """
    Pre-process raw order data and insert into SQLite database.
    
    Extracts only menuItemId from items list and stores as JSON array.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    processed_count = 0
    
    for order in RAW_ORDER_DATA:
        order_id = order["id"]
        restaurant_id = order["restaurantId"]
        
        # Extract only menuItemId from items
        menu_item_ids = [item["menuItemId"] for item in order["items"]]
        
        # Store as JSON string
        items_json = json.dumps(menu_item_ids)
        
        cursor.execute(
            "INSERT OR REPLACE INTO orders (order_id, restaurant_id, items) VALUES (?, ?, ?)",
            (order_id, restaurant_id, items_json)
        )
        processed_count += 1
    
    conn.commit()
    conn.close()
    print(f"✓ Inserted {processed_count} orders into database")


def get_order_history_by_restaurant(restaurant_id: str) -> dict[str, list[str]]:
    """
    Fetch order history for a specific restaurant from SQLite database.
    
    Args:
        restaurant_id: The restaurant ID to filter by
        
    Returns:
        Dictionary mapping order_id to list of menuItemIds
        Format: {"001": ["M101", "M104"], "002": ["M102", "M106"]}
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT order_id, items FROM orders WHERE restaurant_id = ?",
        (restaurant_id,)
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    order_history = {}
    for order_id, items_json in rows:
        order_history[order_id] = json.loads(items_json)
    
    return order_history


def get_all_restaurants() -> list[str]:
    """Get list of all unique restaurant IDs in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT restaurant_id FROM orders ORDER BY restaurant_id")
    rows = cursor.fetchall()
    conn.close()
    
    return [row[0] for row in rows]


def view_database_stats():
    """Print statistics about the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total orders
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    
    # Orders per restaurant
    cursor.execute("""
        SELECT restaurant_id, COUNT(*) as order_count 
        FROM orders 
        GROUP BY restaurant_id 
        ORDER BY restaurant_id
    """)
    restaurant_stats = cursor.fetchall()
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("DATABASE STATISTICS")
    print("=" * 50)
    print(f"Total orders: {total_orders}")
    print(f"Database path: {DB_PATH}")
    print("\nOrders per restaurant:")
    for restaurant_id, count in restaurant_stats:
        print(f"  {restaurant_id}: {count} orders")
    print("=" * 50)


def main():
    """Main function to run the preprocessing pipeline."""
    print("=" * 50)
    print("ORDER DATA PREPROCESSING")
    print("=" * 50)
    
    # Step 1: Create database
    print("\n[1/3] Creating database...")
    create_database()
    
    # Step 2: Pre-process and insert data
    # Commented out by default for development.
    # Uncomment when you want to populate DB from RAW_ORDER_DATA.
    # print("\n[2/3] Processing and inserting data...")
    # preprocess_and_insert_data()
    
    # Step 3: View stats
    print("\n[2/2] Verifying data...")
    view_database_stats()
    
    # Example: Fetch order history for R1
    print("\n" + "=" * 50)
    print("EXAMPLE: Order history for R1")
    print("=" * 50)
    history = get_order_history_by_restaurant("R1")
    for order_id, items in list(history.items())[:3]:
        print(f"  {order_id}: {items}")
    print(f"  ... ({len(history)} orders total)")
    
    print("\n✅ Preprocessing complete!")


if __name__ == "__main__":
    main()
