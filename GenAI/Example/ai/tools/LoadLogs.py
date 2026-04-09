import paramiko
import itertools
import re
import datetime
from langchain.tools import tool
import json
import uuid

def connect_to_ppdm(hostname, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, port=22, username=username, password=password)
    return ssh

def retrieve_loge_from_none_zip_files(ssh, directory, key_word):
    print(f"search logs for key word: \"{key_word}\"")
    # shrimp_cmd = "awk '/^[0-9]{4}-[0-9]{2}-[0-9]{2}/ {if (rec) print rec; rec=$0; next} {rec=rec " " $0} END {print rec}' "
    # stdin, stdout, stderr = ssh.exec_command(f'{shrimp_cmd} {directory}/*.*.log | grep "{key_word}"')
    stdin, stdout, stderr = ssh.exec_command(f'grep -r "{key_word}" {directory}')
    output = stdout.readlines() 
    error = stderr.readlines()
    
    return handle_result(output, error)

def retrieve_loge_from_zip_files(ssh, directory, key_word):
    print(f"search logs in zip logs for keyword: \"{key_word}\"")
    stdin, stdout, stderr = ssh.exec_command(f'find {directory} -name "*.gz" | xargs zgrep "{key_word}"')
    output = stdout.readlines() 
    error = stderr.readlines()

    return handle_result(output, error)
    
def handle_result(output, error):
    if error:
        print("Error occurred:")
        for line in error:
            print(line.strip())
    else:
        print(f"Command executed successfully, got {len(output)} logs")
        return [string.strip() for string in output] 

def is_valid_input(keyword, host):
    
    if(keyword is None or host is None or len(keyword) < 20 or len(host) < 8):
        return False
    
    pattern = r"TRACE_ID:[a-f0-9]+"
    
    if(not is_valid_uuid(keyword) and not re.match(pattern, keyword)):
        return False
    
    return True

@tool
def load_ppdm_logs(keyword:str, ppdm_ip: str) -> str:
    """
        Search PPDM logs, this can be used to analyze the job execution process
        Args:
           host_name(str): the host_name user input, or extract from the case logs or workflow log
           keyword(str): keyword should be resource id or trace id. Resource id is in UUID format, the TRACE_ID is in the format of TRACE_ID:xxxxxxxxx
        
        Returns:
           {
             "logs" -> PPDM logs,
             "trace_ids" -> extraced trace ids, you can use it as keyword to search the log again
            }
    """
    print(f"load_ppdm_logs: search logs hostname:{ppdm_ip}, keyword:\"{keyword}\"")
    hostname=ppdm_ip
    if(not is_valid_input(keyword, hostname)):
        print(f"not valid input to search logs:{ppdm_ip} - {keyword}")
        return  "keyword or host_name is not valid. keyword should be UUID or 'TRACE_ID:[a-f0-9]+'"

    try:
        username="admin"
        password="Changeme@1"
        ssh = connect_to_ppdm(hostname,username,password)

        directory = "/var/log/brs/"
        
        none_zip_logs = retrieve_loge_from_none_zip_files(ssh, directory, keyword)
        zip_logs = retrieve_loge_from_zip_files(ssh, directory, keyword)
        ssh.close()

        all_logs = merge_logs(none_zip_logs, zip_logs)
        # sorted_logs = sort_logs(all_logs)
        if(all_logs is None or len(all_logs) == 0):
            return f"Doesn't found any logs for keyword:\"{keyword}\""
 
        print(f"get total {len(all_logs)} logs")
        
        result = {}
        logs = "\n".join(all_logs)
        result["logs"] = logs
        # if(is_valid_uuid(keyword)):
        #     result["trace_ids"] = find_traceId(logs)
        
        return json.dumps(result)
    
    except Exception as exception:
        print(exception)
        return "get logs error"
    
def merge_logs(none_zip_logs, zip_logs):
    print("merge logs")
    return list(itertools.chain(none_zip_logs, zip_logs))

def find_traceId(logs):
    trace_ids = re.findall(r'(TRACE_ID:[a-f0-9]+)', logs)
    if len(trace_ids) > 0:
        print(f'get trace ids:{trace_ids[0]}')
        return trace_ids[0]
    return trace_ids

def re_search(keyword, logs):
    if(is_valid_uuid(keyword)):
        return reserch_by_trace_id(logs)


def reserch_by_trace_id():
    return

def reserch_by_trace_id():
    return

def sort_logs(logs):
    if(len(logs) == 0):
        return
    
    print("sort logs")
    pattern = r":(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+)Z "
    sorted_logs = sorted(logs, key=lambda x: datetime.datetime.fromisoformat(re.search(pattern, x).group(1)) if re.search(pattern, x) else "1970-01-01T00:00:00.000Z")
    return sorted_logs

def is_valid_uuid(val):
    try:
        # Attempts to create a UUID object from the string
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False   

