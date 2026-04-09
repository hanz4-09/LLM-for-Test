from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from aia_auth import auth
import httpx
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

def load_logs():
    print("load logs")
    """Load Logs to vector"""
    directory_path = "C:\\work\\AI\\Learning\\GenAI\\Example\\logs" 
    loader = DirectoryLoader(
        directory_path,
        glob="**/*.log",
        loader_cls=TextLoader,
        show_progress=True,  # Optional: Show loading progress
        silent_errors=True   # Optional: Skip files that cause errors during loading
    )
    global documents
    documents = loader.load()
    print(f"load {len(documents)} documents")

def split_content():
    print("splite files")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # chunk size (characters)
        chunk_overlap=200,  # chunk overlap (characters)
        separators=["\n"],
        add_start_index=True,  # track index in original document
    )    
    global all_splits
    all_splits = text_splitter.split_documents(documents)
    print(f"extract {len(documents)} documents into {len(all_splits)} chunks")

def init_vector():
    print("init vector")
    global vector_store
    # embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    embeddings = HuggingFaceEmbeddings( 
        show_progress=True,      
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
        model_name=model_name
    )
    vector_store = InMemoryVectorStore(embeddings)
    print(f"adding {len(all_splits)} documents to vector store...")
    vector_store.add_documents(documents=all_splits)
    

# A simple function to get the LLM instance from Dell Digital Cloud Platform
def get_llm_model(model_name):
    http_client = httpx.Client()
    access_token = auth.sso().token
    # access_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImF0LTE2MDk1NTkzNDAiLCJ0eXAiOiJKV1QifQ.eyJpYXQiOjE3NjUyNTgyMDUsImp0aSI6IjU2YzI0ZjI1LWNlYzMtNGM4Yi05Y2QxLTUyMTA5NzQyODBiYSIsInN1YiI6IkouWi5aaGFuZ0BkZWxsLmNvbSIsImNsaWVudF9pZCI6ImExNGI0MDg2LWQ2ODItNGI4MS1hMDdjLTU3ZGE1MTQzN2VmZSIsInByb2ZpbGVpZCI6IjY2OTQ3NzhlLTc1NzUtNDUyZS1hNzE4LTJhODQxYjA2ODk0OSIsIkFEQkRHIjoiMTAzMzE0MSIsImF1dGhzcmMiOiJBRCIsIkFEVU4iOiJ6aGFuZ2o3MCIsIkFERE9NIjoiQVNJQS1QQUNJRklDIiwiUFlTSUQiOiI0NTJjNjMyMi1hZjdkLTRmYWQtYTM1OC1jMWU2MjRjNmNiYWEiLCJFWFRJRFAiOiJUcnVlIiwic3VidHlwZSI6InVzZXIiLCJ0dHkiOiJhdCIsInNjb3BlIjpbImFpYS1nYXRld2F5LmZpbmV0dW5pbmciLCJhaWEtZ2F0ZXdheS5nZW5haS5kZXYiXSwiYXVkIjoiYWlhLWdhdGV3YXkiLCJuYmYiOjE3NjUyNTgyMDUsImV4cCI6MTc2NTI2MDAwNSwiaXNzIjoiaHR0cDovL3d3dy5kZWxsLmNvbS9pZGVudGl0eSJ9.B9oYdcoWEWl2GBtm6Wo9UkK-CmxE7z_JVnCcK8TAz7mvKgSkLuMD26cL_WnClaHxb8CMiHba377N2m-r4UwvmP0jqA2wSqA07Tuiwlfl-0mKx27o46RJhJFgoM60N85Ib3FzRQIw4_ZRKFm-DOReTn3OczysQqbLft0IWnd1b8xFAjpbzKDJPh1BGi8Qdm1YM218dsOyMAeYbDfVn9dxjEG64Xi0pNmLqSoc9uRX71qbDRwfwSvQ2-qXDzMAskVAKkWhbdPfKj6GR-EDeH8qLmLAN49LfXfMUmYs6uTFBGbP81A6tp-fLasNd_4fizFNA2YzXbKTxQ5Q4LmeDaM1cA"
    llm = ChatOpenAI(
        model=model_name,
        base_url="https://aia.gateway.dell.com/genai/dev/v1",
        http_client=http_client,
        api_key=access_token,
    )
    return llm


@tool(response_format="content_and_artifact")
def retrieve_logs(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return retrieved_docs


load_logs()
split_content()
init_vector()

model_name = "gpt-oss-120b"
model = get_llm_model(model_name) # this model is supported by Dell
print("query..")
log_agent = create_agent(
    model,
    tools=[retrieve_logs],
    system_prompt="You have access to a tool that retrieves context from PPDM logs. Use the tool to help answer user queries."
)

query = (
    "TRACE_ID:8ec5e098577f3ba2"
)

for event in log_agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
):
    event["messages"][-1].pretty_print()

# for chunk in log_agent.stream({'messages':[{"role": "user", "content": "TRACE_ID:8ec5e098577f3ba2"}]},stream_mode='values'):
#     print(chunk['messages'])
#     chunk['messages'][-1].pretty_print()