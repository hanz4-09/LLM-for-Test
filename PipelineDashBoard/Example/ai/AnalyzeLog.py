from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import httpx
from tools.CreateFile import create_file

from tools.LoadJenkinsLog import load_jenkins_result

# A simple function to get the LLM instance from Dell Digital Cloud Platform
def get_llm_model(api_key):
    # api_key = get_genapi_key()
    log_model_name = "gpt-oss-120b"
    http_client = httpx.Client()  
    llm = ChatOpenAI(
        model=log_model_name,
        base_url="https://aia.gateway.dell.com/genai/dev/v1",
        http_client=http_client,
        api_key=api_key,
    )
    return llm

def sumarize(api_key):    
    log_model = get_llm_model(api_key)
    
    system_prompt = '''
        You are an expert tester, please create html file contains professional dashboard of the given test result.
        step 1: get test result using load_jenkins_result tool
        step 2: generate the sumarized content， using html5 format, please check the script, be sure there is no jscript error.
        step 3: create html file using create_file tool
    '''    
        
    agent = create_agent(
        model=log_model,
        tools=[load_jenkins_result, create_file],
        system_prompt=system_prompt
    )
 
    agent.invoke(
        {"messages": [{"role": "user", "content": """Please generate a professional dashboard of test reult.
                Title is "Policy Engine Test Result Dashboard - {currentDate}"
                Seprate the statistics by category in order: "Policy","Job Engine", "SUTI".
                In each category:
                       1. Create one table, contains statistics of latest test result of each test suite. The url shown as the build number. Sequence: Total,Passed,Failed,Duration(in hour), url.
                       2. Create pie chart of each test suite, the title is the test suite, contains statistics of latest test result of each test suite, shown 5 charts in one row.
                       3. Create trend chart of each test suite, only including failed count, the title is the test suite, shown 3 trend charts in one row.
                       """
               }]},        
        stream_mode="values",
    )


if __name__ == "__main__":
    api_key = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImF0LTE2MDk1NTkzNDAiLCJ0eXAiOiJKV1QifQ.eyJpYXQiOjE3NzAyODM4MDAsImp0aSI6IjNkZTkxM2VlLTM3ZDAtNGNkOS1hNDgwLTUzYzVhYTYyODBiZiIsInN1YiI6IkouWi5aaGFuZ0BkZWxsLmNvbSIsImNsaWVudF9pZCI6ImExNGI0MDg2LWQ2ODItNGI4MS1hMDdjLTU3ZGE1MTQzN2VmZSIsInByb2ZpbGVpZCI6IjY2OTQ3NzhlLTc1NzUtNDUyZS1hNzE4LTJhODQxYjA2ODk0OSIsIkFEQkRHIjoiMTAzMzE0MSIsImF1dGhzcmMiOiJBRCIsIkFEVU4iOiJ6aGFuZ2o3MCIsIkFERE9NIjoiQVNJQS1QQUNJRklDIiwiUFlTSUQiOiI1M2VjMjgwNC1mY2VmLTQ2NzItOTMwZi0wODUyYTlkZGIzYTYiLCJFWFRJRFAiOiJUcnVlIiwic3VidHlwZSI6InVzZXIiLCJ0dHkiOiJhdCIsInNjb3BlIjpbImFpYS1nYXRld2F5LmFpZGFhcy5kZXYiLCJhaWEtZ2F0ZXdheS5maW5ldHVuaW5nIiwiYWlhLWdhdGV3YXkuZ2VuYWkuZGV2IiwiYWlhLWdhdGV3YXkuZ2VuYWkuZGV2LmJhdGNoIiwiYWlhLWdhdGV3YXkuZ3JvdW5kLXRydXRoIiwiYWlhLWdhdGV3YXkubGxtaiIsImFpYS1nYXRld2F5LnByb21wdC1ldmFsIiwiYWlhLWdhdGV3YXkucHJvbXB0LWdlbiJdLCJhdWQiOiJhaWEtZ2F0ZXdheSIsIm5iZiI6MTc3MDI4MzgwMCwiZXhwIjoxNzcwMjg1NjAwLCJpc3MiOiJodHRwOi8vd3d3LmRlbGwuY29tL2lkZW50aXR5In0.ijJRemlyZVdjnanfuyUH8KYaVC7NTc3fOKzE0L_TxLmP-S-_rwAjC-GPiF_053mRtpW7O1xNbARjt8QeLWp01p0myM6VS7aEtdMZdwuDoTVEWWUmGVhoKsRc6DrSlHLE-rMmUSGdFjRRypsQwNtZGkP0n25dQZ6gRo_l1Q3PaeS4a8tmQXIYNHf9p6RPg_leo7MufxtaxgJAFqDCPWiAHNQa5Snh7c5K2eaIDzc5ftJdB63KEyt78_sWYmpjgbZAy4QAI6aOt3uSE9d_DzZZ0gwvL6RAw3jzVcYRbl2w1TAnzAb9yrLpvfJv9Vjaq4Qcjvu15SBGMRJv7VtZgPCXCw"
    sumarize(api_key)