import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from sqlalchemy.orm import Session

from models import Product, Inventory, Supplier, PurchaseOrder, SalesHistory
from services.forecasting import run_forecast
from services.rop_eoq import calculate_eoq, calculate_rop, days_until_stockout
from services.rag import retrieve_risks_text as retrieve_risks

load_dotenv()

SYSTEM_PROMPT = """You are SupplyMind, an AI supply chain optimization agent.
You have access to tools to check inventory, run demand forecasts, calculate reorder points,
retrieve risk intelligence, and generate purchase orders.

Always reason step-by-step:
1. Check current stock levels
2. Run demand forecast to estimate future need
3. Calculate ROP and EOQ
4. Check for supply risks
5. Draft a Purchase Order if stock is below ROP

Use the following format:
Thought: your reasoning
Action: tool name
Action Input: input to the tool
Observation: tool result
... (repeat as needed)
Thought: I now have enough information
Final Answer: your complete recommendation

{tools}

{tool_names}

{agent_scratchpad}

Question: {input}"""


def build_agent(db: Session):

    def check_inventory(product_name: str) -> str:
        p = db.query(Product).filter(Product.name.ilike(f"%{product_name}%")).first()
        if not p:
            return f"Product '{product_name}' not found."
        inv = db.query(Inventory).filter(Inventory.product_id == p.id).first()
        stock = inv.stock if inv else 0
        return (
            f"Product: {p.name} | Stock: {stock} {p.unit} | "
            f"Reorder Point: {p.reorder_point} | Lead Time: {p.lead_time_days} days"
        )

    def forecast_demand(product_name: str) -> str:
        p = db.query(Product).filter(Product.name.ilike(f"%{product_name}%")).first()
        if not p:
            return f"Product '{product_name}' not found."
        forecasts = run_forecast(db, p.id, periods=14)
        if not forecasts or "error" in forecasts[0]:
            return "Forecast unavailable — insufficient data."
        avg = sum(f["predicted_demand"] for f in forecasts) / len(forecasts)
        peak = max(f["predicted_demand"] for f in forecasts)
        return f"{p.name} — 14-day avg demand: {avg:.1f}/day, peak: {peak:.1f}/day"

    def get_rop_eoq(product_name: str) -> str:
        p = db.query(Product).filter(Product.name.ilike(f"%{product_name}%")).first()
        if not p:
            return f"Product '{product_name}' not found."
        rows = db.query(SalesHistory).filter(SalesHistory.product_id == p.id).all()
        if not rows:
            return "No sales data available."
        avg_daily = sum(r.quantity_sold for r in rows) / len(rows)
        annual = avg_daily * 365
        rop = calculate_rop(avg_daily, p.lead_time_days)
        eoq = calculate_eoq(annual, p.order_cost, p.holding_cost)
        inv = db.query(Inventory).filter(Inventory.product_id == p.id).first()
        stock = inv.stock if inv else 0
        days_left = days_until_stockout(stock, avg_daily)
        return (
            f"{p.name} — ROP: {rop}, EOQ: {eoq}, "
            f"Avg daily demand: {avg_daily:.1f}, Days until stockout: {days_left}"
        )

    def risk_intelligence(query: str) -> str:
        risks = retrieve_risks(query)
        return "Relevant risks:\n" + "\n".join(f"- {r}" for r in risks)

    def generate_po(product_name: str) -> str:
        p = db.query(Product).filter(Product.name.ilike(f"%{product_name}%")).first()
        if not p:
            return f"Product '{product_name}' not found."
        rows = db.query(SalesHistory).filter(SalesHistory.product_id == p.id).all()
        avg_daily = sum(r.quantity_sold for r in rows) / len(rows) if rows else 10
        annual = avg_daily * 365
        eoq = calculate_eoq(annual, p.order_cost, p.holding_cost)

        # Pick best supplier: score = reliability / (price * lead_time)
        suppliers = db.query(Supplier).filter(Supplier.product_id == p.id).all()
        if not suppliers:
            return f"No suppliers found for {p.name}."
        best = max(suppliers, key=lambda s: s.reliability_score / (s.price_per_unit * s.lead_time_days))

        po = PurchaseOrder(
            product_id=p.id,
            supplier_id=best.id,
            quantity=eoq,
            status="Draft",
            reason=(
                f"Stock below ROP. EOQ={eoq} units ordered from {best.name} "
                f"(price={best.price_per_unit}, lead={best.lead_time_days}d, reliability={best.reliability_score})"
            ),
        )
        db.add(po)
        db.commit()
        return (
            f"✅ PO #{po.id} drafted — Order {eoq} {p.unit} of {p.name} "
            f"from {best.name} at ${best.price_per_unit}/{p.unit}. "
            f"Lead time: {best.lead_time_days} days. Total: ${eoq * best.price_per_unit:.2f}"
        )

    tools = [
        Tool(name="CheckInventory",    func=check_inventory,  description="Check current stock for a product. Input: product name."),
        Tool(name="ForecastDemand",    func=forecast_demand,  description="Run Prophet demand forecast for a product. Input: product name."),
        Tool(name="GetROPandEOQ",      func=get_rop_eoq,      description="Calculate Reorder Point and EOQ for a product. Input: product name."),
        Tool(name="RiskIntelligence",  func=risk_intelligence,description="Retrieve supply chain risk context. Input: risk query string."),
        Tool(name="GeneratePO",        func=generate_po,      description="Generate a Purchase Order for a product. Input: product name."),
    ]

    openai_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_key or openai_key == "your_openai_api_key_here":
        # Fallback rule-based agent when no OpenAI key
        return None, tools

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=8), tools


def run_agent_query(db: Session, query: str) -> str:
    executor, tools = build_agent(db)

    if executor is None:
        # Rule-based fallback
        tool_map = {t.name: t for t in tools}
        results = []
        for product in ["Rice", "Sugar", "Coffee Beans", "Wheat Flour", "Cooking Oil"]:
            inv_info = tool_map["CheckInventory"].func(product)
            rop_info = tool_map["GetROPandEOQ"].func(product)
            results.append(f"{inv_info}\n{rop_info}")

        # Auto-generate POs for critical items
        po_results = []
        for product in ["Rice", "Sugar"]:
            po = tool_map["GeneratePO"].func(product)
            po_results.append(po)

        risk = tool_map["RiskIntelligence"].func(query)
        return "\n\n".join(results) + "\n\n" + "\n".join(po_results) + "\n\n" + risk

    try:
        result = executor.invoke({"input": query})
        return result.get("output", "No response generated.")
    except Exception as e:
        return f"Agent error: {str(e)}"
