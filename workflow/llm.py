# The AI model shared by all agents

from langchain_openai import ChatOpenAI

from config import OPENAI_MODEL

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)
