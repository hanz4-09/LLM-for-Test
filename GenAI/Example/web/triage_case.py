import streamlit as st
from Example.ai.AnalyzeLog import analyze_case_llm
from langchain_core.messages import AIMessage

st.set_page_config(layout="wide")
st.title("Triage Automation Cases")
            

def generate_case_response(api_key, ppdm_ip, input_text):
    response = analyze_case_llm(api_key, ppdm_ip, input_text)
    for chunk in response: 
            if("messages" in chunk and chunk["messages"] is not None and len(chunk["messages"]) > 0): 
                if(isinstance(chunk["messages"], list)):
                    message = chunk["messages"][-1]
                    if(isinstance(message, AIMessage)):
                        yield message.content
                else:
                     yield message     

with st.form("case_form"):
    api_key = st.text_area("Enter the GenAI key(you can get it from SSO_APIKey_Generator):")
    ppdm_ip = st.text_input("Enter the ppdm ip (**Optional**, such as: 10.198.19.68) :", type="default")
    jenkins_rul = st.text_area("Enter the jenkins url(just copy link of the failed case, such as:https://idpsppdm-jenkins.cec.lab.emc.com/job/ecdm/job/Policy-Engine/job/Policy-Engine-Daily-DUTI/job/Job-Executor-Automation/job/Job-Executor-Component-Test/1072/testReport/junit/(root)/Job%20Executor%20Data%20Consistency%20Test/Test_for_JobExecution_cancellation_retry_after_service_restart/) :")
    
    submitted = st.form_submit_button("Analyze")
    if not api_key:
        st.warning("Please enter your api key!", icon="⚠")
    if submitted and api_key:
        st.write_stream(generate_case_response(api_key, ppdm_ip, jenkins_rul))        