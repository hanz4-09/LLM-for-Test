import streamlit as st
import json
from Example.ai.AnalyzeLog import analyze_bug_llm

st.title("Triage Bug")
api_key = st.text_area("Enter the GenAI key(you can get it from SSO_APIKey_Generator):")
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.chat_message("assistant"):
        st.markdown("Good Day! What can I do for you?")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input():
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
         token = analyze_bug_llm(api_key, st) 
    
    with st.chat_message("assistant"):        
        ai_message = token["messages"][-1]        
        st.markdown(ai_message.content)
        st.session_state.messages.append({"role": "assistant", "content": ai_message.content})

