import sys

SPEED = 0.5
START_TIME = 480.0
TIME_LIMIT = 30.0
REWARD_PER_ORDER = 10
def parse_order(line, order_index, preorder_count):

    parts = line.split()
    order = {
        "id": int(parts[0]),
        "t": float(parts[1]),
        "sx": float(parts[2]),
        "sy": float(parts[3]),
        "ex": float(parts[4]),
        "ey": float(parts[5]),
    }

    if order_index < preorder_count:
        order["type"] = "pre-order"
    else:
        order["type"] = "instant-order"

    return order


def parse_input(text):

    lines = []

    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    first_line = lines[0].split()
    length = float(first_line[0])
    width = float(first_line[1])
    courier_count = int(first_line[2])
    preorder_count = int(first_line[3])

    orders = []

    for order_index, line in enumerate(lines[1:]):
        order = parse_order(line, order_index, preorder_count)
        orders.append(order)
    return {
        "length": length,
        "width": width,
        "courier_count": courier_count,
        "preorder_count": preorder_count,
        "orders": orders,
    }

