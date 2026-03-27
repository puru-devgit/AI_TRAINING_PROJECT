from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# create prompt
prompt = PromptTemplate(
    input_variables=["item", "stock"],
    template="If stock of {item} is {stock}, should we reorder? Answer yes or no."
)

# create model
llm = OpenAI(temperature=0.7)

# create chain
chain = LLMChain(llm=llm, prompt=prompt)

# run test
response = chain.run({"item": "Rice", "stock": 10})

print(response)