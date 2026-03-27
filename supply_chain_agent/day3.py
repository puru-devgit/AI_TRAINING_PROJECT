from langchain.llms import OpenAI

llm = OpenAI(temperature=0.7)

def smart_reorder_decision(item, stock, forecast_demand):
    
    # rule 1: low stock
    if stock < 20:
        return f"⚠️ Low stock for {item}. Reorder immediately."
    
    # rule 2: high future demand
    if forecast_demand > stock:
        return f"📈 Demand for {item} is HIGH. Reorder soon."
    
    # else use AI reasoning
    prompt = f"""
    Item: {item}
    Current Stock: {stock}
    Forecast Demand: {forecast_demand}
    
    Should we reorder? Give a short answer.
    """
    
    response = llm(prompt)
    
    return response


# test cases
print(smart_reorder_decision("Rice", 10, 50))
print(smart_reorder_decision("Wheat", 40, 100))
print(smart_reorder_decision("Sugar", 100, 50))