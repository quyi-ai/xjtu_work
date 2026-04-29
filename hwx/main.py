import sys

SPEED = 0.5
START_TIME = 480.0
TIME_LIMIT = 30.0
REWARD_PER_ORDER = 10
def parse_order(line):

    parts = line.split()
    order = {
        "id": int(parts[0]),
        "t": float(parts[1]),
        "sx": float(parts[2]),
        "sy": float(parts[3]),
        "ex": float(parts[4]),
        "ey": float(parts[5]),
    }

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
        order = parse_order(line)

        if order_index < preorder_count:
            order["type"] = "pre-order"
        else:
            order["type"] = "instant-order"

        orders.append(order)

    return {
        "length": length,
        "width": width,
        "courier_count": courier_count,
        "preorder_count": preorder_count,
        "orders": orders,
    }

def create_couriers(courier_count):
    couriers=[]
    for i in range(courier_count):
        couriers.append({'id':i+1,'x':0,'y':0,'available_time':START_TIME})
    return couriers


def manhattan_distance(x1,y1,x2,y2):
    return abs(x1-x2)+abs(y1-y2)

def calc_preorder_delivery(courier, order):
    x,y=courier['x'],courier['y']
    sx,sy=order['sx'],order['sy']
    ex,ey=order['ex'],order['ey']

    dis_to_pick=manhattan_distance(x,y,sx,sy)
    time_to_pick=dis_to_pick/SPEED
    arrive_at_pick=courier['available_time']+time_to_pick
    pick_time=max(arrive_at_pick,order['t'])
    dis_delivery=manhattan_distance(sx,sy,ex,ey)
    time_to_delivery=dis_delivery/SPEED
    delivery_time=time_to_delivery+pick_time
    return delivery_time