from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import PurchaseOrder, Product, Supplier

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/")
def list_orders(db: Session = Depends(get_db)):
    orders = db.query(PurchaseOrder).order_by(PurchaseOrder.created_at.desc()).limit(500).all()
    result = []
    for o in orders:
        p = db.query(Product).filter(Product.id == o.product_id).first()
        s = db.query(Supplier).filter(Supplier.id == o.supplier_id).first()
        result.append({
            "id": o.id,
            "product": p.name if p else "Unknown",
            "supplier": s.name if s else "Unknown",
            "quantity": o.quantity,
            "status": o.status,
            "reason": o.reason,
            "created_at": o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else "",
        })
    return result
