from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routers import inventory, forecast, agent, orders, weather, risks
from seed import seed

app = FastAPI(title="SupplyMind AI", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed()


app.include_router(inventory.router)
app.include_router(forecast.router)
app.include_router(agent.router)
app.include_router(orders.router)
app.include_router(weather.router)
app.include_router(risks.router)


@app.get("/")
def root():
    return {"message": "SupplyMind AI backend running ✅"}
