import json
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


# ============================================================
# SUPERMARKET INVENTORY AND SALES MANAGEMENT SYSTEM
# ============================================================

INVENTORY_FILE = "inventory.json"
SALES_FILE = "sales.json"
CURRENCY = "EGP"


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def money(value):
    """Convert a value to Decimal with two decimal places."""
    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def format_money(value):
    """Format a value as currency."""
    return f"{money(value):,.2f} {CURRENCY}"


def input_non_empty(prompt):
    """Get a non-empty string from the user."""
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("Input cannot be empty.")


def input_integer(prompt, minimum=None):
    """Get a valid integer from the user."""
    while True:
        try:
            value = int(input(prompt).strip())

            if minimum is not None and value < minimum:
                print(f"Please enter a value greater than or equal to {minimum}.")
                continue

            return value

        except ValueError:
            print("Please enter a valid whole number.")


def input_decimal(prompt, minimum=None, maximum=None):
    """Get a valid decimal number from the user."""
    while True:
        try:
            value = money(input(prompt).strip())

            if minimum is not None and value < money(minimum):
                print(f"Please enter a value greater than or equal to {minimum}.")
                continue

            if maximum is not None and value > money(maximum):
                print(f"Please enter a value less than or equal to {maximum}.")
                continue

            return value

        except (InvalidOperation, ValueError):
            print("Please enter a valid number.")


def input_yes_no(prompt):
    """Get a yes/no answer."""
    while True:
        answer = input(prompt).strip().lower()

        if answer in ("y", "yes"):
            return True

        if answer in ("n", "no"):
            return False

        print("Please enter Y or N.")


def pause():
    input("\nPress Enter to continue...")


# ============================================================
# FILE HANDLING
# ============================================================

def save_json(filename, data):
    """Save data to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except OSError as error:
        print(f"Error saving {filename}: {error}")
        return False


def load_json(filename, default):
    """Load data from a JSON file."""
    if not os.path.exists(filename):

        if save_json(filename, default):
            return default

        return default

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)

    except (OSError, json.JSONDecodeError) as error:
        print(f"Warning: Could not read {filename}.")
        print(f"Reason: {error}")

        return default


def load_inventory():
    """Load inventory from inventory.json."""
    inventory = load_json(INVENTORY_FILE, [])

    if not isinstance(inventory, list):
        return []

    return inventory


def load_sales():
    """Load sales history from sales.json."""
    sales = load_json(SALES_FILE, [])

    if not isinstance(sales, list):
        return []

    return sales


# ============================================================
# INVENTORY SEARCH
# ============================================================

def find_by_barcode(inventory, barcode):
    """Find an item using its barcode."""
    barcode = str(barcode).strip()

    for item in inventory:
        if item["barcode"] == barcode:
            return item

    return None


def find_by_name(inventory, name):
    """Find an item by exact or unique partial name."""
    target = name.strip().lower()

    # Exact match
    for item in inventory:
        if item["name"].lower() == target:
            return item

    # Partial match
    matches = []

    for item in inventory:
        if target in item["name"].lower():
            matches.append(item)

    if len(matches) == 1:
        return matches[0]

    return None


def find_partial_matches(inventory, name):
    """Return all items matching part of a name."""
    target = name.strip().lower()

    return [
        item
        for item in inventory
        if target in item["name"].lower()
    ]


# ============================================================
# PRICE AND DISCOUNT CALCULATIONS
# ============================================================

def calculate_sale_price(item):
    """
    Calculate final item price after discount.
    """
    price = money(item["price"])
    discount = money(item.get("discount", 0))

    if discount < 0:
        discount = Decimal("0")

    if discount > 100:
        discount = Decimal("100")

    sale_price = price * (
        Decimal("1") - discount / Decimal("100")
    )

    return money(sale_price)


def calculate_saving_per_item(item):
    """Calculate how much the customer saves per item."""
    original_price = money(item["price"])
    sale_price = calculate_sale_price(item)

    return money(original_price - sale_price)


# ============================================================
# DISPLAY INVENTORY
# ============================================================

def display_item(item):
    """Display detailed information about one item."""

    price = money(item["price"])
    discount = money(item.get("discount", 0))
    sale_price = calculate_sale_price(item)

    print("\n----------------------------------------")
    print(f"Barcode       : {item['barcode']}")
    print(f"Name          : {item['name']}")
    print(f"Category      : {item['category']}")
    print(f"Original Price: {format_money(price)}")
    print(f"Discount      : {discount}%")
    print(f"Sale Price    : {format_money(sale_price)}")
    print(f"Stock         : {item['stock']}")
    print("----------------------------------------")


def display_inventory(inventory):
    """Display all inventory items."""

    if not inventory:
        print("\nInventory is empty.")
        return

    print("\n" + "=" * 110)

    print(
        f"{'Barcode':<15}"
        f"{'Name':<25}"
        f"{'Category':<18}"
        f"{'Price':>15}"
        f"{'Discount':>12}"
        f"{'Sale Price':>15}"
        f"{'Stock':>8}"
    )

    print("=" * 110)

    sorted_inventory = sorted(
        inventory,
        key=lambda item: item["name"].lower()
    )

    for item in sorted_inventory:

        price = money(item["price"])
        discount = money(item.get("discount", 0))
        sale_price = calculate_sale_price(item)

        print(
            f"{item['barcode']:<15}"
            f"{item['name'][:24]:<25}"
            f"{item['category'][:17]:<18}"
            f"{format_money(price):>15}"
            f"{str(discount) + '%':>12}"
            f"{format_money(sale_price):>15}"
            f"{item['stock']:>8}"
        )

    print("=" * 110)


# ============================================================
# CREATE - ADD ITEM
# ============================================================

def add_item(inventory):
    """Add a new item to inventory."""

    print("\n========== ADD NEW ITEM ==========")

    while True:
        barcode = input_non_empty("Barcode: ")

        if find_by_barcode(inventory, barcode):
            print("This barcode already exists.")
        else:
            break

    name = input_non_empty("Item name: ")

    category = input_non_empty("Category: ")

    price = input_decimal(
        "Original price: ",
        minimum=0
    )

    stock = input_integer(
        "Initial stock quantity: ",
        minimum=0
    )

    discount = input_decimal(
        "Discount percentage (0-100): ",
        minimum=0,
        maximum=100
    )

    item = {
        "barcode": barcode,
        "name": name,
        "category": category,
        "price": str(price),
        "stock": stock,
        "discount": str(discount)
    }

    inventory.append(item)

    if save_json(INVENTORY_FILE, inventory):
        print("\nItem added successfully.")
    else:
        inventory.remove(item)
        print("\nItem could not be saved.")


# ============================================================
# READ - FIND ITEM
# ============================================================

def find_item_menu(inventory):
    """Search for an item by barcode or name."""

    print("\n========== FIND ITEM ==========")
    print("1. Search by barcode")
    print("2. Search by name")

    choice = input("Choose: ").strip()

    if choice == "1":

        barcode = input_non_empty(
            "Enter barcode: "
        )

        item = find_by_barcode(
            inventory,
            barcode
        )

        if item:
            display_item(item)
        else:
            print("Item not found.")

    elif choice == "2":

        name = input_non_empty(
            "Enter item name: "
        )

        item = find_by_name(
            inventory,
            name
        )

        if item:
            display_item(item)

        else:

            matches = find_partial_matches(
                inventory,
                name
            )

            if len(matches) > 1:

                print("\nMultiple items found:")

                for index, match in enumerate(
                    matches,
                    start=1
                ):
                    print(
                        f"{index}. "
                        f"{match['name']} "
                        f"(Barcode: {match['barcode']})"
                    )

            else:
                print("Item not found.")

    else:
        print("Invalid choice.")


# ============================================================
# UPDATE ITEM
# ============================================================

def update_item(inventory):
    """Update an existing inventory item."""

    print("\n========== UPDATE ITEM ==========")

    barcode = input_non_empty(
        "Enter barcode of item to update: "
    )

    item = find_by_barcode(
        inventory,
        barcode
    )

    if not item:
        print("Item not found.")
        return

    print("\nCurrent information:")
    display_item(item)

    print("\nPress Enter to keep the current value.")

    old_item = item.copy()

    new_name = input(
        f"Name [{item['name']}]: "
    ).strip()

    new_category = input(
        f"Category [{item['category']}]: "
    ).strip()

    new_price = input(
        f"Price [{item['price']}]: "
    ).strip()

    new_stock = input(
        f"Stock [{item['stock']}]: "
    ).strip()

    new_discount = input(
        f"Discount [{item.get('discount', 0)}]: "
    ).strip()

    try:

        if new_name:
            item["name"] = new_name

        if new_category:
            item["category"] = new_category

        if new_price:
            price = money(new_price)

            if price < 0:
                raise ValueError

            item["price"] = str(price)

        if new_stock:
            stock = int(new_stock)

            if stock < 0:
                raise ValueError

            item["stock"] = stock

        if new_discount:
            discount = money(new_discount)

            if discount < 0 or discount > 100:
                raise ValueError

            item["discount"] = str(discount)

    except (ValueError, InvalidOperation):

        item.clear()
        item.update(old_item)

        print("Invalid information. No changes were saved.")
        return

    if save_json(INVENTORY_FILE, inventory):
        print("\nItem updated successfully.")

    else:

        item.clear()
        item.update(old_item)

        print("Could not save changes.")


# ============================================================
# DELETE ITEM
# ============================================================

def delete_item(inventory):
    """Delete an item from inventory."""

    print("\n========== DELETE ITEM ==========")

    barcode = input_non_empty(
        "Enter barcode of item to delete: "
    )

    item = find_by_barcode(
        inventory,
        barcode
    )

    if not item:
        print("Item not found.")
        return

    display_item(item)

    confirmation = input_yes_no(
        "\nAre you sure you want to delete this item? (Y/N): "
    )

    if not confirmation:
        print("Deletion cancelled.")
        return

    index = inventory.index(item)

    removed_item = inventory.pop(index)

    if save_json(INVENTORY_FILE, inventory):
        print("\nItem deleted successfully.")

    else:
        inventory.insert(index, removed_item)
        print("Could not save deletion.")


# ============================================================
# ORDERING SYSTEM
# ============================================================

def select_product(inventory):
    """
    Allow the customer to select a product using
    its name or barcode.
    """

    value = input(
        "\nEnter item name or barcode "
        "(or type 'done'): "
    ).strip()

    if value.lower() == "done":
        return "done"

    # Search barcode first
    item = find_by_barcode(
        inventory,
        value
    )

    if item:
        return item

    # Search name
    item = find_by_name(
        inventory,
        value
    )

    if item:
        return item

    # Multiple partial matches
    matches = find_partial_matches(
        inventory,
        value
    )

    if len(matches) > 1:

        print("\nMultiple products match:")

        for index, match in enumerate(
            matches,
            start=1
        ):
            print(
                f"{index}. "
                f"{match['name']} | "
                f"Barcode: {match['barcode']} | "
                f"Stock: {match['stock']} | "
                f"Sale Price: "
                f"{format_money(calculate_sale_price(match))}"
            )

        while True:

            try:

                choice = int(
                    input(
                        "Select product number "
                        "(0 to cancel): "
                    )
                )

                if choice == 0:
                    return None

                if 1 <= choice <= len(matches):
                    return matches[choice - 1]

                print("Invalid selection.")

            except ValueError:
                print("Enter a valid number.")

    print("Item not found.")
    return None


def create_order(inventory, sales):
    """Create a customer order and update stock."""

    print("\n========== NEW ORDER ==========")

    if not inventory:
        print("Inventory is empty.")
        return

    cart = []

    while True:

        item = select_product(inventory)

        if item == "done":
            break

        if item is None:
            continue

        if item["stock"] <= 0:
            print(
                f"{item['name']} is out of stock."
            )
            continue

        sale_price = calculate_sale_price(item)
        saving = calculate_saving_per_item(item)

        print("\nSelected product:")
        print(f"Name          : {item['name']}")
        print(f"Barcode       : {item['barcode']}")
        print(f"Original Price: {format_money(item['price'])}")
        print(f"Discount      : {item.get('discount', 0)}%")
        print(f"Sale Price    : {format_money(sale_price)}")
        print(f"Saving/Item   : {format_money(saving)}")
        print(f"Available     : {item['stock']}")

        # Check quantity already in cart
        quantity_in_cart = 0

        for cart_item in cart:

            if cart_item["barcode"] == item["barcode"]:
                quantity_in_cart = cart_item["quantity"]

        remaining = item["stock"] - quantity_in_cart

        if remaining <= 0:
            print(
                "All available stock is already in your cart."
            )
            continue

        quantity = input_integer(
            f"Quantity (1-{remaining}): ",
            minimum=1
        )

        if quantity > remaining:
            print("Not enough stock available.")
            continue

        # Add or update cart
        existing = None

        for cart_item in cart:

            if cart_item["barcode"] == item["barcode"]:
                existing = cart_item
                break

        if existing:

            existing["quantity"] += quantity

            existing["line_total"] = money(
                existing["quantity"]
                * existing["unit_price"]
            )

            existing["discount_amount"] = money(
                existing["quantity"]
                * existing["saving_per_item"]
            )

        else:

            line_total = money(
                quantity * sale_price
            )

            discount_amount = money(
                quantity * saving
            )

            cart.append(
                {
                    "barcode": item["barcode"],
                    "name": item["name"],
                    "quantity": quantity,
                    "unit_price": sale_price,
                    "regular_unit_price": money(
                        item["price"]
                    ),
                    "saving_per_item": saving,
                    "discount_amount": discount_amount,
                    "line_total": line_total
                }
            )

        print(
            f"{quantity} x {item['name']} "
            "added to cart."
        )

    if not cart:
        print("No products were added.")
        return

    # Calculate totals
    subtotal = money(
        sum(
            (
                item["regular_unit_price"]
                * item["quantity"]
                for item in cart
            ),
            Decimal("0")
        )
    )

    total_discount = money(
        sum(
            (
                item["discount_amount"]
                for item in cart
            ),
            Decimal("0")
        )
    )

    total = money(
        subtotal - total_discount
    )

    # ========================================================
    # RECEIPT
    # ========================================================

    print("\n")
    print("=" * 75)
    print("                    MINI MARKET")
    print("                    SALES RECEIPT")
    print("=" * 75)

    print(
        "Date:",
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    print("-" * 75)

    print(
        f"{'Product':<25}"
        f"{'Qty':>6}"
        f"{'Unit Price':>15}"
        f"{'Discount':>12}"
        f"{'Total':>15}"
    )

    print("-" * 75)

    for item in cart:

        print(
            f"{item['name'][:24]:<25}"
            f"{item['quantity']:>6}"
            f"{format_money(item['unit_price']):>15}"
            f"{format_money(item['discount_amount']):>12}"
            f"{format_money(item['line_total']):>15}"
        )

    print("-" * 75)

    print(
        f"{'Subtotal:':<58}"
        f"{format_money(subtotal):>17}"
    )

    print(
        f"{'Total Savings:':<58}"
        f"{format_money(total_discount):>17}"
    )

    print(
        f"{'TOTAL TO PAY:':<58}"
        f"{format_money(total):>17}"
    )

    print("=" * 75)

    # Confirm purchase
    confirm = input_yes_no(
        "\nConfirm purchase? (Y/N): "
    )

    if not confirm:
        print(
            "Purchase cancelled. "
            "Stock was not changed."
        )
        return

    # Check stock one more time before updating
    for cart_item in cart:

        inventory_item = find_by_barcode(
            inventory,
            cart_item["barcode"]
        )

        if (
            inventory_item is None
            or inventory_item["stock"]
            < cart_item["quantity"]
        ):

            print(
                "Purchase failed because "
                "the stock is no longer sufficient."
            )
            return

    # ========================================================
    # UPDATE STOCK
    # ========================================================

    for cart_item in cart:

        inventory_item = find_by_barcode(
            inventory,
            cart_item["barcode"]
        )

        inventory_item["stock"] -= cart_item["quantity"]

    # ========================================================
    # SAVE SALE
    # ========================================================

    sale = {
        "sale_id": len(sales) + 1,
        "date": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "items": [],
        "subtotal": str(subtotal),
        "total_discount": str(total_discount),
        "total": str(total)
    }

    for cart_item in cart:

        sale["items"].append(
            {
                "barcode": cart_item["barcode"],
                "name": cart_item["name"],
                "quantity": cart_item["quantity"],
                "unit_price": str(
                    cart_item["unit_price"]
                ),
                "line_total": str(
                    cart_item["line_total"]
                )
            }
        )

    # Save updated inventory
    if not save_json(
        INVENTORY_FILE,
        inventory
    ):

        # Roll back stock if save fails
        for cart_item in cart:

            inventory_item = find_by_barcode(
                inventory,
                cart_item["barcode"]
            )

            if inventory_item:
                inventory_item["stock"] += (
                    cart_item["quantity"]
                )

        print(
            "Purchase failed because "
            "inventory could not be saved."
        )

        return

    # Save sale history
    sales.append(sale)

    if not save_json(
        SALES_FILE,
        sales
    ):

        print(
            "\nPurchase completed and stock updated."
        )

        print(
            "Warning: sales history could not be saved."
        )

        return

    print("\nPurchase completed successfully!")

    print(
        f"Total paid: {format_money(total)}"
    )

    print(
        f"Total savings: {format_money(total_discount)}"
    )


# ============================================================
# SALES HISTORY
# ============================================================

def show_sales_history(sales):
    """Display previous sales."""

    print("\n========== SALES HISTORY ==========")

    if not sales:
        print("No sales recorded yet.")
        return

    for sale in reversed(sales):

        print("\n----------------------------------------")

        print(
            f"Sale ID: {sale.get('sale_id', 'N/A')}"
        )

        print(
            f"Date: {sale.get('date', 'Unknown')}"
        )

        print("----------------------------------------")

        for item in sale.get("items", []):

            print(
                f"{item.get('name', 'Unknown')} | "
                f"Qty: {item.get('quantity', 0)} | "
                f"Unit: "
                f"{format_money(item.get('unit_price', 0))} | "
                f"Total: "
                f"{format_money(item.get('line_total', 0))}"
            )

        print(
            f"Subtotal: "
            f"{format_money(sale.get('subtotal', 0))}"
        )

        print(
            f"Savings: "
            f"{format_money(sale.get('total_discount', 0))}"
        )

        print(
            f"Total: "
            f"{format_money(sale.get('total', 0))}"
        )


# ============================================================
# SAMPLE DATA
# ============================================================

def create_sample_inventory():
    """
    Create sample inventory for first-time use.
    This is only used when inventory.json is empty.
    """

    sample_items = [

        {
            "barcode": "100001",
            "name": "Milk 1 Liter",
            "category": "Dairy",
            "price": "45.00",
            "stock": 30,
            "discount": "5.00"
        },

        {
            "barcode": "100002",
            "name": "White Bread",
            "category": "Bakery",
            "price": "20.00",
            "stock": 40,
            "discount": "0.00"
        },

        {
            "barcode": "100003",
            "name": "Potato Chips",
            "category": "Snacks",
            "price": "35.00",
            "stock": 25,
            "discount": "10.00"
        },

        {
            "barcode": "100004",
            "name": "Orange Juice",
            "category": "Beverages",
            "price": "60.00",
            "stock": 20,
            "discount": "15.00"
        },

        {
            "barcode": "100005",
            "name": "Tuna Can",
            "category": "Canned Food",
            "price": "55.00",
            "stock": 15,
            "discount": "8.00"
        }

    ]

    save_json(
        INVENTORY_FILE,
        sample_items
    )

    return sample_items


# ============================================================
# MAIN MENU
# ============================================================

def display_menu():
    """Display the main application menu."""

    print("\n")
    print("=" * 60)
    print("       SUPERMARKET INVENTORY & SALES SYSTEM")
    print("=" * 60)

    print("1. View all inventory")
    print("2. Add new item")
    print("3. Find item")
    print("4. Update item")
    print("5. Delete item")
    print("6. Create new order / sale")
    print("7. View sales history")
    print("8. Exit")

    print("=" * 60)


def main():
    """Main application function."""

    print("=" * 60)
    print(" Welcome to the Supermarket Management System")
    print("=" * 60)

    # Load data
    inventory = load_inventory()
    sales = load_sales()

    # Create sample data on first run
    if not inventory:

        inventory = create_sample_inventory()

        print(
            "\nSample inventory created successfully."
        )

        print(
            f"Data is stored in: {INVENTORY_FILE}"
        )

    while True:

        display_menu()

        choice = input(
            "Enter your choice: "
        ).strip()

        if choice == "1":

            display_inventory(
                inventory
            )

            pause()

        elif choice == "2":

            add_item(
                inventory
            )

            pause()

        elif choice == "3":

            find_item_menu(
                inventory
            )

            pause()

        elif choice == "4":

            update_item(
                inventory
            )

            pause()

        elif choice == "5":

            delete_item(
                inventory
            )

            pause()

        elif choice == "6":

            create_order(
                inventory,
                sales
            )

            pause()

        elif choice == "7":

            show_sales_history(
                sales
            )

            pause()

        elif choice == "8":

            print(
                "\nThank you for using "
                "the Supermarket Management System!"
            )

            break

        else:

            print(
                "\nInvalid choice. "
                "Please select 1-8."
            )


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\n\nProgram stopped by user."
        )

    except Exception as error:

        print(
            "\nAn unexpected error occurred:"
        )

        print(error)