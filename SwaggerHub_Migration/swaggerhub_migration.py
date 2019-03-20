'''
Created on Mar 19, 2019

@author: Steven.Colon
'''
import requests
import json
import helper_functions


with open('config.json', 'r') as file:
    config = json.load(file)

export_org_api_key= config['EXPORTORG']['API_KEY']
export_org_registry_basepath = config['EXPORTORG']['REGISTRY_API_BASEPATH']
export_org_name = config['EXPORTORG']['ORG']

import_org_api_key= config['IMPORTORG']['API_KEY']
import_org_registry_basepath = config['IMPORTORG']['REGISTRY_API_BASEPATH']
import_org_name = config['IMPORTORG']['ORG']

def main():
    #URL to pull/push API Specs
    export_org_registry_api = export_org_registry_basepath +"apis/"
    import_org_registry_api = import_org_registry_basepath + "apis/"
        
    #Pull specs in the outgoing org
    org_specs_call = requests.get(export_org_registry_api + export_org_name, headers= {'Authorization': export_org_api_key})
    org_apis_json = org_specs_call.json()
    
    if len(org_apis_json['apis']) == 0:
        raise RuntimeError("No APIs Found in SAAS Org")
    
    print("Migrating " + str(org_apis_json["totalCount"]) + " OAS Specs from " + export_org_registry_api + export_org_name + " to " + import_org_registry_api + import_org_name)
    
    parse_org(org_apis_json, export_org_registry_api, import_org_registry_api)
    
    
    export_org_domains_url = export_org_registry_basepath + "domains/"
    import_org_domains_url = import_org_registry_basepath + "domains/"
    
    export_org_domains_call = requests.get(export_org_domains_url + export_org_name, headers= {'Authorization': export_org_api_key})
    
    export_org_domains_json = export_org_domains_call.json()
    
    print("Migrating " + str(export_org_domains_json["totalCount"]) + " Domains from " + export_org_registry_api + export_org_name + " to " + import_org_registry_api + import_org_name +"\n\n")
    
    parse_org(export_org_domains_json, export_org_domains_url, import_org_domains_url)

def parse_org(org_json, export_url, import_url):
    for metadata in org_json["apis"]:
        #Remove Default Version number from API Url so that we can pull all versions
        url = metadata["properties"][0]["url"] 
        last_slash = url.rindex('/', 0)
        formatted_url = url[0: last_slash]
        formatted_url = helper_functions.verify_http_type(formatted_url, export_url)
        
            
        sh_name = formatted_url[formatted_url.rindex('/', 0) + 1 : len(formatted_url)]
        print("Name - " + sh_name)
        print("Pulling versions from " + formatted_url)
    
        #Pull json that shows each version of the spec 
        versions_call= requests.get(formatted_url, headers={'Authorization': export_org_api_key})
        versions_json = versions_call.json()
    
        print("Found " + str(versions_json["totalCount"]) + " versions ...")
        
        export_versions(versions_json, sh_name, export_url, import_url)

def export_versions(versions_json, sh_name, export_url, import_url):
    #Pull API Version URLs
    for version in versions_json['apis']:
        api_version_url = helper_functions.verify_http_type(version["properties"][0]["url"], export_url)
        print(api_version_url)
        version_number = version["properties"][1]["value"]
        #Get spec of single API Version
        api_version_spec_call = requests.get(api_version_url, headers = {'Authorization': export_org_api_key})
        #print("Status of API Version Spec Call - " +  str(api_version_spec_call.status_code))
        
        #push spec to OnPrem 
        import_org_post_url = import_url + import_org_name + "/" + sh_name + '?isPrivate=true&version=' + version_number
        
        print("Posting Spec to - " + import_org_post_url)
        
        import_version(import_org_post_url, api_version_spec_call)
            
    print("\n")
        
        
def import_version(import_org_post_url, api_version_spec_call):
    onprem_post_call = requests.post(import_org_post_url, headers={'Authorization': import_org_api_key}, json=api_version_spec_call.json())
        
    if(onprem_post_call.status_code != 201 and onprem_post_call.status_code != 200):
        raise RuntimeError("Invalid OnPrem API Response - " + onprem_post_call.text)
    else:
        print("API Version Uploaded to OnPrem")
        
main()

    


        

