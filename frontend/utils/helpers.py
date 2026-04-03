def calculate_status(stock, reorder_point):
    if stock < reorder_point:
        return "🔴 Critical"
    elif stock < reorder_point * 1.5:
        return "🟡 Low"
    return "🟢 Safe"


def format_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(round(num, 1))


def detect_risk(stock, reorder_point):
    if stock < reorder_point:
        return "⚠️ High risk of stockout!"
    elif stock < reorder_point * 1.5:
        return "⚠️ Moderate risk"
    return "✅ Low risk"
