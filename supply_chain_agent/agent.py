import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

os.environ["GOOGLE_API_KEY"] = "AIzaSyDEDU7AtXnqXCC5B9vilQPF18am4a96BGA"

prompt = ChatPromptTemplate.from_template("""
You are an intelligent supply chain assistant.

Rules:
- If stock < forecast → Reorder
- If risk is high → prioritize ordering more
- If stock >= forecast → No Reorder

Inputs:
Item: {item}
Stock: {stock}
Forecast: {forecast}
Risk: {risk}

Give output in this format:
Decision: <Reorder / No Reorder>
Reason: <short explanation>
""")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

parser = StrOutputParser()

chain = prompt | llm | parser

# TEST CASE 1
result1 = chain.invoke({
    "item": "rice",
    "stock": 5,
    "forecast": 20,
    "risk": "low"
})
print(result1)

# TEST CASE 2
result2 = chain.invoke({
    "item": "rice",
    "stock": 30,
    "forecast": 20,
    "risk": "low"
})
print(result2)

# TEST CASE 3
result3 = chain.invoke({
    "item": "rice",
    "stock": 10,
    "forecast": 20,
    "risk": "high"
})
print(result3)