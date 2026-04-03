import pandas as pd
from prophet import Prophet
from sqlalchemy.orm import Session
from models import SalesHistory, Product


def run_forecast(db: Session, product_id: int, periods: int = 30) -> list[dict]:
    rows = (
        db.query(SalesHistory.sale_date, SalesHistory.quantity_sold)
        .filter(SalesHistory.product_id == product_id)
        .order_by(SalesHistory.sale_date)
        .all()
    )

    if len(rows) < 30:
        return []

    df = pd.DataFrame(rows, columns=["ds", "y"])
    df["ds"] = pd.to_datetime(df["ds"])

    try:
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.80,
        )
        model.fit(df)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
    except Exception as e:
        return [{"error": str(e)}]

    result = forecast[["ds", "yhat", "yhat_upper", "yhat_lower"]].tail(periods)
    return [
        {
            "date": row.ds.strftime("%Y-%m-%d"),
            "predicted_demand": round(max(0, row.yhat), 2),
            "upper": round(max(0, row.yhat_upper), 2),
            "lower": round(max(0, row.yhat_lower), 2),
        }
        for row in result.itertuples()
    ]
