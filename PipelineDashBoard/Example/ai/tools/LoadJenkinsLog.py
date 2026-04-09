import jenkins
from bs4 import BeautifulSoup
from langchain.tools import tool
import json
from langchain.tools import ToolRuntime
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

target_folders = [
        'ecdm/Policy-Engine/Policy-Engine-Daily-DUTI',
        'ecdm/Policy-Engine/PLC-Core-Daily-SUTI'
        ]

all_monitored_jobs ={
    "Job-Executor-Component-Test":"Job Engine",
    "Job-Creator-Component-Test":"Job Engine",
    "Job-Dispatcher-Component-Test":"Job Engine",
    "10.198.19.192-JobEngine-E2E":"Job Engine",
    "10.198.19.195-Resource-Management":"Job Engine",
    "Execution-Planner-Component-Test":"Policy",
    "Central-Interpreter-Component-Test":"Policy",
    "Scheduler-Component-Test":"Policy",
    "PolicyV3Component":"Policy",
    "Script-Component-Test":"Policy",    
    "10.198.19.193-Mock":"SUTI",
    "10.198.19.194-Cucumber":"SUTI",
    "10.198.19.198-VM":"SUTI",
    "10.198.19.56-CucumberNew":"SUTI",
    "10.198.19.208-SelfService":"SUTI"    
}

# @tool
def load_jenkins_result() -> json:
    """
        Tool to get the test result.
        Args:
           no argument.
        
        Returns:
          test result: json string including the test result, array of test suites
    """
     
    try:
        JENKINS_URL = 'https://idpsppdm-jenkins.cec.lab.emc.com/'
        JENKINS_USER = 'zhangj70'
        JENKINS_TOKEN = '11627df686bdae0d6d59f419a69f3f444f'
        server = jenkins.Jenkins(JENKINS_URL, username=JENKINS_USER, password=JENKINS_TOKEN)

        jobs = server.get_all_jobs()
        

        sub_jobs = [
            job for job in jobs if is_monitored_job(job["fullname"]) and 'folder' not in job.get('_class', '').lower()
        ]
        
        test_report = []
        trend_history_depth = 7
        for job in sub_jobs:           
            job_info = server.get_job_info(job["fullname"])            
            job_results={}
            job_results["suite"] = job["name"]
            job_results["category"] = all_monitored_jobs.get(job["name"], None)
            job_results["url"] = job.get("url", None)
            job_results["result"] = []
            last_build_number = job_info.get('lastBuild')['number']
            
            for build in range(last_build_number - trend_history_depth, last_build_number + 1):
                test_results = server.get_build_test_report(job["fullname"], build)               
                if test_results is not None:       
                    build_info = server.get_build_info(job["fullname"], build)  
                    dt_object = datetime.fromtimestamp(build_info.get('timestamp', None) / 1000.0)               
                    test_results["build"] = dt_object.strftime('%m/%d')                               
                    test_results.pop('suites', None)
                    # print(f"build test report:{test_results}")  
                    test_results.pop('_class', None)
                    test_results.pop('testActions', None)
                    test_results.pop('empty', None)                    
                    pass_count=test_results.get("passCount", 0)
                    faile_count=test_results.get("failCount", 0)
                    skip_count=test_results.get("skipCount", 0)
                    total_count=pass_count + faile_count + skip_count
                    test_results["totalCount"] = total_count
                    job_results["result"].append(test_results)
            test_report.append(job_results)    
        # print(f"test report:{test_report}")    
        return json.dumps(test_report)    

    except jenkins.JenkinsException as e:
        print(f"Error connecting to Jenkins: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

 
def is_monitored_job(fullName) -> bool:
    return any(fullName.startswith(folder) for folder in target_folders) and any(fullName.endswith(monitored) for monitored in all_monitored_jobs.keys())

if __name__ == "__main__":     
    load_jenkins_result()
