from langchain.llms import OpenAI

# create model
llm = OpenAI(temperature=0.7)

# function to decide reorder
def check_reorder(item, stock):
    
    # simple rule (VERY IMPORTANT)
    if stock < 20:
        return f"⚠️ Stock for {item} is LOW. Reorder needed."
    
    # else ask AI
    prompt = f"Stock of {item} is {stock}. Should we reorder?"
    
    response = llm(prompt)
    
    return response


# test cases
print(check_reorder("Rice", 10))
print(check_reorder("Wheat", 50))