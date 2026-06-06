from langgraph.graph import StateGraph,START,END
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os

os.environ['LANGCHAIN_PROJECT'] = 'ChatBot_Project'

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

connect = sqlite3.connect(database='chatbot.db',check_same_thread=False)
checkpoint = SqliteSaver(conn=connect)

chatbot = graph.compile(checkpointer=checkpoint)
def retrive_all_threads():
 all_threads = set()
 for chckpoint in checkpoint.list(None):
    all_threads.add(chckpoint.config['configurable']['thread_id'])
 return (list(all_threads))



#test
# CONFIG = {'configurable': {'thread_id': '2-id'}}
# response = chatbot.stream(
#                 {'messages': [HumanMessage(content='can you tell my name')]},
#                 config= CONFIG,
#             )
# print(list(response))