import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
import json
from langchain.tools import ToolRuntime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@tool
def load_jenkins_log_1(runtime: ToolRuntime) -> json:
    """
        Get the details of case
        The jenkins_url is accessed via runtime

        Returns:
           JSON string:
            {
                "case_name": int,
                "status": str,
                "ErrorMessage": str,
                "StackTrace": str,
                "logs": str
            }                    
    """
    
    try:
        url = runtime.context.get("jenkins_url") 
        print(f"load jenkins logs from url: {url}")
        auth = ('zhangj70', '11627df686bdae0d6d59f419a69f3f444f')
        response = requests.get(url, auth=auth)
        soup = BeautifulSoup(response.content, 'html.parser')
        # header = soup.find()
        main_div = soup.find("div", {"id": "main-panel"})
        case_details = {}
        if main_div:            
            main_content= main_div.find('p')
            clean_html_content(main_content)             
            case_position = main_content.text.find("Error Message")
            case = main_content.text[:case_position].strip()
            # print(f"---->case:{case}")
            case_details["case_name"] = case
            status =   main_div.find('h1') 
            # print(f"status:{status.text}")
            case_details["status"] = status.text
            contents = main_content.find_all('pre')
            error_message=contents[0]
            case_details["ErrorMessage"] = error_message.text
            # print(f"----> error message:{error_message.text}")
            stack_trace=contents[1]
            # print(f"----> StackTrace:{stack_trace.text}")
            case_details["StackTrace"] = stack_trace.text
            logs=contents[2]
            # print(f"----> logs:{logs.text}")
            case_details["logs"] = logs.text
            # print(main_div)         
        
        if(len(case_details) == 0):
            print("Doesn't found case details")
            return "Doesn't found case details"
        else:
            return json.dumps(case_details)
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"not found case logs for jenkins url:{jenkins_url}"
    
# @tool
def load_jenkins_log(jenkins_url: str) -> str:
    """
        Get the details of case

        Args:
           jenkins_url(str): the jenkins url to get the details of the case

        Returns:
           JSON string:
            {
                "case_name": int,
                "status": str,
                "ErrorMessage": str,
                "StackTrace": str,
                "logs": str
            }                    
    """
    
    try:
        url = jenkins_url 
        print(f"load jenkins logs from url: {url}")
        auth = ('zhangj70', '11627df686bdae0d6d59f419a69f3f444f')
        response = requests.get(url, auth=auth, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        # header = soup.find()
        main_div = soup.find("div", {"id": "main-panel"})
        case_details = {}
        if main_div:            
            main_content= main_div.find('p')
            clean_html_content(main_content)             
            case_position = main_content.text.find("Error Message")
            case = main_content.text[:case_position].strip()
            # print(f"---->case:{case}")
            case_details["case_name"] = case
            status =   main_div.find('h1') 
            # print(f"status:{status.text}")
            case_details["status"] = status.text
            contents = main_content.find_all('pre')
            error_message=contents[0]
            case_details["ErrorMessage"] = error_message.text
            # print(f"----> error message:{error_message.text}")
            stack_trace=contents[1]
            # print(f"----> StackTrace:{stack_trace.text}")
            case_details["StackTrace"] = stack_trace.text
            logs=contents[2]
            # print(f"----> logs:{logs.text}")
            case_details["logs"] = logs.text
            # print(main_div)         
        
        if(len(case_details) == 0):
            print("Doesn't found case details")
            return "Doesn't found case details"
        else:
            return json.dumps(case_details)
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"not found case logs for jenkins url:{jenkins_url}"
    
def clean_html_content(root_div):
    for div_tag in root_div.find_all("div"):
                div_tag.decompose()
    useless_table = root_div.find("table")
    useless_table.decompose()

if __name__ == "__main__":
     
    jenkins_url="https://idpsppdm-jenkins.cec.lab.emc.com/job/ecdm/job/Policy-Engine/job/Policy-Engine-Daily-DUTI/job/Job-Creator-Automation/job/Job-Creator-Component-Test/1272/testReport/junit/(root)/Basic%20Job%20Creator%20Component%20Test/Test_Jobs_Creation_rebuild_for_NAS___job_not_created_/"

    load_jenkins_log(jenkins_url)

# try:
#     JENKINS_URL = 'https://idpsppdm-jenkins.cec.lab.emc.com/'
#     JENKINS_USER = 'zhangj70'
#     JENKINS_TOKEN = '11627df686bdae0d6d59f419a69f3f444f'
#     server = jenkins.Jenkins(JENKINS_URL, username=JENKINS_USER, password=JENKINS_TOKEN)
#     user = server.get_whoami()
#     version = server.get_version()
#     print(f'Hello {user["fullName"]} from Jenkins version {version}')

#     # Example: List all jobs
#     jobs = server.get_jobs()
#     print(f'Found {len(jobs)} jobs.')
#     for job in jobs:
#         print(f'- {job}')

# except jenkins.JenkinsException as e:
#     print(f"Error connecting to Jenkins: {e}")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")

# try:
#     # Get the test results for a specific build
#     # This uses the built-in Jenkins API endpoint for test reports
#     JOB_NAME = 'Your-Python-Test-Job'
#     BUILD_NUMBER = 1 # The build number you want results for
#     test_results = server.get_build_test_report(JOB_NAME, BUILD_NUMBER)
    
#     print(test_results)
#     # Print summary information
#     print(f"Total tests: {test_results['passCount'] + test_results['failCount'] + test_results['skipCount']}")
#     print(f"Passed: {test_results['passCount']}")
#     print(f"Failed: {test_results['failCount']}")
#     print(f"Skipped: {test_results['skipCount']}")
    
# except jenkins.NotFoundException:
#     print(f"Test results not found for build #{BUILD_NUMBER}. Ensure the 'Publish JUnit test result report' post-build action ran successfully.")
# except Exception as e:
#     print(f"An error occurred: {e}")