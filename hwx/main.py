import sys


def parse_order(line, order_index, preorder_count):
    """
    Parse one order line.

    Each order line has 6 fields:
    id t sx sy ex ey
    """
    parts = line.split()

    if len(parts) != 6:
        raise ValueError(f"Order line must have 6 fields, got {len(parts)}: {line}")

    order = {
        "id": int(parts[0]),
        "time": float(parts[1]),
        "pickup_x": float(parts[2]),
        "pickup_y": float(parts[3]),
        "delivery_x": float(parts[4]),
        "delivery_y": float(parts[5]),
    }

    if order_index < preorder_count:
        order["type"] = "pre-order"
    else:
        order["type"] = "instant-order"

    return order


def parse_input(text):
    """
    Parse all input from stdin.

    Input format:
    First line: L W n m
    Following lines: id t sx sy ex ey
    """
    lines = []

    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)

    if not lines:
        raise ValueError("Input is empty.")

    first_line = lines[0].split()

    if len(first_line) != 4:
        raise ValueError("First line must have 4 fields: L W n m")

    length = float(first_line[0])
    width = float(first_line[1])
    courier_count = int(first_line[2])
    preorder_count = int(first_line[3])

    orders = []

    for order_index, line in enumerate(lines[1:]):
        order = parse_order(line, order_index, preorder_count)
        orders.append(order)

    if len(orders) < preorder_count:
        raise ValueError("The number of order lines is less than m.")

    return {
        "length": length,
        "width": width,
        "courier_count": courier_count,
        "preorder_count": preorder_count,
        "orders": orders,
    }


def print_debug_summary(data):
    """
    Print parsed data so we can check whether reading works.

    This is only a temporary output for learning and debugging.
    The real scheduling output will be added later.
    """
    print("Parsed input successfully.")
    print(f"Area: L={data['length']:.2f}, W={data['width']:.2f}")
    print(f"Couriers: {data['courier_count']}")
    print(f"Pre-orders: {data['preorder_count']}")
    print(f"Total orders: {len(data['orders'])}")

    for order in data["orders"]:
        print(
            "Order "
            f"{order['id']}: "
            f"type={order['type']}, "
            f"time={order['time']:.2f}, "
            f"pickup=({order['pickup_x']:.2f}, {order['pickup_y']:.2f}), "
            f"delivery=({order['delivery_x']:.2f}, {order['delivery_y']:.2f})"
        )


def main():
    input_text = sys.stdin.read()
    data = parse_input(input_text)

    # Temporary: show parsed data.
    # Later, replace this line with the scheduling algorithm and official output.
    print_debug_summary(data)


if __name__ == "__main__":
    main()
