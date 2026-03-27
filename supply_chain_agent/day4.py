from langchain.llms import OpenAI

llm = OpenAI(temperature=0.7)

# function to create purchase order
def create_purchase_order(item, quantity):
    return f"🧾 PO CREATED: Order {quantity} units of {item}"

# main agent function
def supply_chain_agent(item, stock, forecast_demand):
    
    # decision 1: low stock
    if stock < 20:
        return create_purchase_order(item, 100)
    
    # decision 2: demand higher than stock
    if forecast_demand > stock:
        order_qty = forecast_demand - stock
        return create_purchase_order(item, order_qty)
    
    # else AI decision
    prompt = f"""
    Item: {item}
    Stock: {stock}
    Forecast Demand: {forecast_demand}
    
    Should we reorder? If yes, suggest quantity.
    """
    
    response = llm(prompt)
    
    return response


# test cases
print(supply_chain_agent("Rice", 10, 50))
print(supply_chain_agent("Wheat", 40, 100))
print(supply_chain_agent("Sugar", 100, 50))