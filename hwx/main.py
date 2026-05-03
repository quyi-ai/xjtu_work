import sys

SPEED = 0.5
START_TIME = 480.0
TIME_LIMIT = 30.0
REWARD_PER_ORDER = 10
def parse_order(line):#处理订单，返回订单列表
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


def parse_input(text):#处理输入，返回字典

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

def create_couriers(courier_count):#创建外卖员，返回列表
    couriers=[]
    for i in range(courier_count):
        couriers.append({'id':i+1,'x':0,'y':0,'available_time':START_TIME})
    return couriers


def manhattan_distance(x1,y1,x2,y2):#计算距离
    return abs(x1-x2)+abs(y1-y2)

def calc_preorder_delivery(order, courier):#计算外卖员送预订单时间
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

def calc_instant_delivery(order,courier):#计算外卖员送即时订单时间
    x,y=courier['x'],courier['y']
    sx,sy=order['sx'],order['sy']
    ex,ey=order['ex'],order['ey']

    dis_to_pick=manhattan_distance(x,y,sx,sy)
    time_to_pick=dis_to_pick/SPEED
    start_time = max(courier['available_time'], order['t'])
    pick_time = start_time + time_to_pick
    dis_delivery=manhattan_distance(sx,sy,ex,ey)
    time_to_delivery=dis_delivery/SPEED
    delivery_time=time_to_delivery+pick_time
    return delivery_time
    
def is_success(order,delivery_time):#判断按时送达
    if delivery_time<=TIME_LIMIT+order['t']:
        return True
    else:
        return False
def choose_best_courier(order,couriers):#选择合适的外卖员，返回外卖员和送达时间
    best_courier = None
    best_delivery_time = None
    for courier in couriers:
        if order['type']=='pre-order':
            delivery_time=calc_preorder_delivery(order,courier)
        else:
            delivery_time=calc_instant_delivery(order,courier)
        if is_success(order,delivery_time):
            if best_courier==None or (best_delivery_time>delivery_time):
                best_courier=courier
                best_delivery_time=delivery_time
    return best_courier,best_delivery_time
def assign_order(order,courier,delivery_time):#修改外卖员状态
    courier['available_time']=delivery_time
    courier['x']=order['ex']
    courier['y']=order['ey']

def schedule_orders(orders,couriers):#按顺序处理所有订单，返回结果和统计
    results=[]
    total_completed=0
    for order in orders:
        best_courier,best_delivery_time=choose_best_courier(order,couriers)
        if best_courier==None:
            results.append(
                {
                "id": order["id"],
                "courier_id": 0,
                "delivery_time": -1.0,
                "success": 0,
                }
            )
        else:
            assign_order(order,best_courier,best_delivery_time)
            results.append(
                {
                    'id':order['id'],
                    'courier_id':best_courier['id'],
                    'delivery_time':best_delivery_time,
                    'success':1
                }
            )
            total_completed+=1
    total_revenue=total_completed*REWARD_PER_ORDER
    return results,total_completed,total_revenue

def print_results(results,total_completed,total_revenue):#输出每个订单结果和总收入
    for result in results:
            print(
                result["id"],
                result["courier_id"],
                f'{result["delivery_time"]:.2f}',
                result["success"]
                )
            print(total_completed, f"{total_revenue:.2f}")
def main():#主函数，组织整个程序运行
    input_text = sys.stdin.read()

    data = parse_input(input_text)

    couriers = create_couriers(data["courier_count"])

    results, total_completed, total_revenue = schedule_orders(
        data["orders"],
        couriers
    )

    print_results(results, total_completed, total_revenue)


if __name__ == "__main__":
    main()
