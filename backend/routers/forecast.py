from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Product, SalesHistory
from services.forecasting import run_forecast

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/")
def forecast(
    product_id: int = Query(1),
    periods: int = Query(30),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    data = run_forecast(db, product_id, periods)
    return {"product": product.name, "forecast": data}


@router.get("/sales")
def sales_history(product_id: int = Query(1), db: Session = Depends(get_db)):
    rows = (
        db.query(SalesHistory)
        .filter(SalesHistory.product_id == product_id)
        .order_by(SalesHistory.sale_date)
        .all()
    )
    return [{"date": r.sale_date.strftime("%Y-%m-%d"), "quantity_sold": r.quantity_sold} for r in rows]
