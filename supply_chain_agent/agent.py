import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


os.environ["GOOGLE_API_KEY"] = "AIzaSyDKdjlLu93zmnl8WK7g6FJP206pJALVcLw"

prompt = ChatPromptTemplate.from_template("""
You are a supply chain assistant.

If stock of {item} is less than 10:
Say: "Alert: Reorder required"

If stock is 10 or more:
Say: "Stock is sufficient"

Stock: {stock}
""")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

parser = StrOutputParser()

chain = prompt | llm | parser

result1 = chain.invoke({
    "item": "rice",
    "stock": 5
})
print(result1)

result2 = chain.invoke({
    "item": "rice",
    "stock": 20
})
print(result2)