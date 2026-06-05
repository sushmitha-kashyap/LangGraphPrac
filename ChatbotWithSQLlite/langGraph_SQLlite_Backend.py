from langgraph.graph import StateGraph,START,END
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id = "Qwen/Qwen2.5-7B-Instruct",
    task = "conversational"
 )

model = ChatHuggingFace(llm = llm)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state:ChatState):
    # take user query from state
    messages = state['messages']
    # send to llm
    response = model.invoke(messages)
    # response store state
    return {'messages':[response]}

graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node', END)

checkpoint = InMemorySaver()

chatbot = graph.compile(checkpointer=checkpoint)
