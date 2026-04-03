from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Product, Inventory, SalesHistory
from services.rop_eoq import calculate_rop, days_until_stockout

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/")
def list_inventory(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    result = []
    for p in products:
        inv = db.query(Inventory).filter(Inventory.product_id == p.id).first()
        stock = inv.stock if inv else 0
        rows = db.query(SalesHistory).filter(SalesHistory.product_id == p.id).all()
        avg_daily = sum(r.quantity_sold for r in rows) / len(rows) if rows else 10
        rop = calculate_rop(avg_daily, p.lead_time_days)
        days_left = days_until_stockout(stock, avg_daily)
        result.append({
            "id": p.id,
            "product": p.name,
            "category": p.category,
            "stock": stock,
            "unit": p.unit,
            "reorder_point": round(rop, 1),
            "lead_time": p.lead_time_days,
            "avg_daily_demand": round(avg_daily, 2),
            "days_to_stockout": days_left,
        })
    return result


@router.put("/{product_id}/stock")
def update_stock(product_id: int, stock: float, db: Session = Depends(get_db)):
    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inv:
        return {"error": "Not found"}
    inv.stock = stock
    db.commit()
    return {"message": "Stock updated", "product_id": product_id, "new_stock": stock}
