from elasticsearch import Elasticsearch, NotFoundError
import json
from langchain.tools import tool

index_map = {
    "activity":"index_activity_v3",
    "asset":"index_asset",
    "policy":"index_policy",
    "infrastructure_object":"index_infrastructure_object",
    "execution-plans":"index_execution_plan",
    "schedules":"index_schedule_v3",
    "exported_copy_metadata":"index_exported_copy_v3",
    "copy":"index_protection_copy_set",
    "data target":"index_storage_target"
}
def connect_to_es(hostname):
    es = Elasticsearch(f"http://{hostname}:14300")
    return es

def get_resource(es, type, id):
    print(f"get {type} resource by \"{id}\"")
    index_name=index_map[type]
    try:
       res = es.get(index=index_name, id=id) 
       es.transport.close()
       return json.dumps(res["_source"])
    except NotFoundError:
        return None

            
def query_all_activities(es, id):
    activities = []
    index_name= index_map["activity"]
    activity = get_resource(es, activity, id)
    if activity is not None:
        query_body = {
            "query": {
                "match": {
                    "ancestryId": activity["ancestryId"]
                }
            },
            "size": 50  # Request 10 documents (default is also 10)
        }
    
        response = es.search(index=index_name, body=query_body)
        if(response['hits']['total']['value'] > 0):
            hits = response["hits"]["hits"]
            for hit in hits:
                activities.append(hit["_source"])
    es.transport.close()
    return json.dumps(activities)


@tool
def load_ES_data(ppdm_ip: str, resource_type:str, resource_id:str) -> str:
    """
        Get the resource details, by the resource type and resource id

        Args:
           ppdm_ip(str): the ppdm_ip user input, or extract from the case logs or workflow log
           resource_type(str): the resource type, can be one of ["activity","asset","policy","infrastructure_object"]
           resource_id: the resource id
        Returns:
           the resource get from Elasticsearch, json string, could be array                   
    """
    print(f"load_ES_data tool: hostname:{ppdm_ip}, resource type:\"{resource_type}\", resource id:\"{resource_id}\"")
    try:

        if(resource_type is None or resource_id is None or ppdm_ip is None or len(resource_id) < 10 or len(ppdm_ip) < 8):
            return "the parameter should not be empty"
      
        if resource_type not in index_map.keys:
             return "no matched resource type"
        
        es = connect_to_es(ppdm_ip)        
        
        if resource_type == "activity":
            return query_all_activities(es, resource_id)
        else:
            return get_resource(es, resource_type, resource_id)
        
    except Exception as exception:
        print(exception)
        return f"not found resource by type {resource_type} and id {resource_id}"


    
