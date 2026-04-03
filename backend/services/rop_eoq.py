import math


def calculate_rop(avg_daily_demand: float, lead_time_days: int, safety_stock: float = 0) -> float:
    """Reorder Point = (avg daily demand × lead time) + safety stock"""
    return round(avg_daily_demand * lead_time_days + safety_stock, 2)


def calculate_eoq(annual_demand: float, order_cost: float, holding_cost: float) -> float:
    """Economic Order Quantity = sqrt(2 * D * S / H)"""
    if holding_cost <= 0 or annual_demand <= 0:
        return 0
    return round(math.sqrt((2 * annual_demand * order_cost) / holding_cost), 2)


def days_until_stockout(stock: float, avg_daily_demand: float) -> float:
    if avg_daily_demand <= 0:
        return float("inf")
    return round(stock / avg_daily_demand, 1)
