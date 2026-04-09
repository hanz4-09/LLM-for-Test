from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import httpx
from Example.ai.tools.LoadLogs import load_ppdm_logs 
from Example.ai.tools.LoadEsData import load_ES_data
from Example.ai.tools.LoadJenkinsLog import load_jenkins_log
import os

def get_genapi_key():
    # access_token = auth.sso().token 
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjM4YTcwN2RiLTlmMTQtNGQ2Zi1hZjY3LTM5YWQ3YTMwNWNiNyJ9._SwwK2o7G_vy-jpb57oWVidkVpYSX9xszU-h7_n3j_M"
    # client_id="d478e82a-4824-452e-bf7e-ffdf2e17a5b3"
    # client_secret="2A6C61B12691D6E439D77B55D07882506989F2FD20AB0C5A15824F9DD56E47B76BEA066C7DCAF4E0BC89A8"
    # access_token=auth.client_credentials(client_id, client_secret).token

    return access_token

def get_tool_instructions() -> str:
    elasticsearch_tool_instructions = load_prompt("Example/ai/elasticsearch_tool_prompt.md")
    log_tool_instructions = load_prompt("Example/ai/log_tool_prompt.md")

    return "\n" + elasticsearch_tool_instructions + "\n" + log_tool_instructions + "\n"

def load_prompt(file_name: str) -> str:
    current_dir = os.path.abspath(os.getcwd())
    file_path = os.path.join(current_dir, file_name)
    with open(file_path, "r") as f:
        return f.read()
    
# A simple function to get the LLM instance from Dell Digital Cloud Platform
def get_llm_model(api_key):
    # api_key = get_genapi_key()
    log_model_name = "gpt-oss-120b"
    http_client = httpx.Client()  
    llm = ChatOpenAI(
        model=log_model_name,
        base_url="https://aia.gateway.dell.com/genai/dev/v1",
        # base_url = "http://127.0.0.1:8790/",
        http_client=http_client,
        api_key=api_key,
    )
    return llm

def analyze_log_llm(api_key, ppdm_ip, query):    
    log_model = get_llm_model(api_key)
    
    system_prompt = '''
        You are an expert PPDM Log Analysis Assistant. You can analyze the PPDM user problems using two tools: load_ppdm_logs and load_ES_data.
    '''    
    system_prompt += "\n" + get_tool_instructions()
    
    log_agent = create_agent(
        model=log_model,
        tools=[load_ppdm_logs, load_ES_data],
        system_prompt=system_prompt
    )

    return log_agent.stream(
        {"messages": [{"role": "user", "content": query + f" host_name:{ppdm_ip}"}]},        
        stream_mode="values",
    )

def analyze_case_llm(api_key, ppdm_ip, jenkins_url):
    case_model = get_llm_model(api_key)

    system_prompt = '''
        You are an expert Test Case Analysis Assistant. You can analyze the test case using two tools: load_ppdm_logs and load_ES_data.
        The test case is run as jenkins job, test case run on docker node, test bed is PPDM.
    '''    
    system_prompt += "\n" + get_tool_instructions()
    
    case_agent = create_agent(
        model= case_model,
        tools=[load_ES_data, load_ppdm_logs],
        system_prompt= system_prompt       
    )
    
    case_details = load_jenkins_log(jenkins_url)
    return case_agent.stream(
        {"messages": [ {"role": "user", "content": f"Test case details: {case_details}"},
                       {"role": "user", "content": f"If you can't get the PPDM ip from the test case details, this is the PPDM ip: {ppdm_ip}"}
                      ]},       
                       
        stream_mode="values"
    )

def analyze_bug_llm(api_key, st):
    llm_model = get_llm_model(api_key)

    system_prompt = '''
        You are an expert programming assistant. Please help answer technical questions.
    '''    
    bug_agent = create_agent(
        model = llm_model,
        system_prompt = system_prompt       
    )    

    stream = bug_agent.stream(
        {"messages": [ 
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages       
        ]},
        stream_mode="values"
    )

    for token in stream:
        pass
 
    return token

if __name__ == "__main__":
    query = (
        "why job a2282424-2bf5-4d84-b4f5-8abed34b168d could not been retried?"
    )

    host_name = "10.198.19.68"
    for event in analyze_log_llm(host_name, query):
        # print(event)        
        event["messages"][-1].pretty_print()
