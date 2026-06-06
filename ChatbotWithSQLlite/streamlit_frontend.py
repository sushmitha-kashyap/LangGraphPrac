import streamlit as st
from langGraph_SQLlite_Backend import chatbot, retrive_all_threads
from langchain_core.messages import HumanMessage
import uuid

#utility function
def generate_thread_id():
    thread_id=uuid.uuid4()
    return thread_id

def reset_chat():
    st.session_state['thread_id']=generate_thread_id() #generates new thread_id
    st.session_state['message_history']=[] #new empty message history list
    add_thread(st.session_state['thread_id'])

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_convos(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=retrive_all_threads()
add_thread(st.session_state['thread_id'])

st.sidebar.title('ChatBot LangGraph')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
  if st.sidebar.button(str(thread_id)):
      st.session_state['thread_id']=thread_id
      msg = load_convos(thread_id)

      temp_msg = []

      for each_msg in msg:
          if isinstance(each_msg, HumanMessage):
              role = 'user'
          else:
              role = 'assistant'
          temp_msg.append({'role':role, 'content': each_msg.content})
      st.session_state['message_history']=temp_msg


# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input('Type here')
CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}


if user_input:
    #add user input to message history
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('assistant'):
     ai_response = st.write_stream(
         message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= CONFIG,
                stream_mode= 'messages'
            )
    )

    st.session_state['message_history'].append({'role':'assistant','content':ai_response})
