import streamlit as st
from langchain_core.messages import AIMessage
from Example.ai.AnalyzeLog import analyze_log_llm

st.title("Analyze Logs")

def generate_only_logs_response(api_key, ppdm_ip, input_text):
    response = analyze_log_llm(api_key, ppdm_ip, input_text)
    for chunk in response: 
            if("messages" in chunk and chunk["messages"] is not None and len(chunk["messages"]) > 0): 
                if(isinstance(chunk["messages"], list)):
                    message = chunk["messages"][-1]
                    if(isinstance(message, AIMessage)):
                        yield message.content
                else:
                     yield message                        


with st.form("only_logs_form"):
    api_key = st.text_area("Enter the GenAI key(you can get it from SSO_APIKey_Generator):")
    ppdm_ip = st.text_input("Enter the ppdm ip (such as: 10.198.19.68) optional:", type="default")

    query = st.text_area(
        "Enter question:(such as: why job a2282424-2bf5-4d84-b4f5-8abed34b168d could not been retried?)",
    )
    submitted = st.form_submit_button("Ask")
    if not ppdm_ip or not api_key:
        st.warning("Please enter your PPDM IP and api key!", icon="⚠")
    if submitted and ppdm_ip:
        st.write_stream(generate_only_logs_response(api_key, ppdm_ip, query))
