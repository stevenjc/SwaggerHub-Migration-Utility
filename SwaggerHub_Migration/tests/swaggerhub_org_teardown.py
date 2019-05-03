'''
Created on Mar 19, 2019

@author: Steven.Colon
'''


#IMPORTANT NOTE - THIS SCRIPT WILL DELETE EVERY SPEC IN A ORG
import requests
import json
import helper_functions

input("WARNING - This Script will delete all API specs from a SwaggerHub Org. Press Enter to continue ...")
with open('../config.json', 'r') as file:
    config = json.load(file)
    
import_org_api_key= config['IMPORTORG']['API_KEY']
import_org_registry_basepath = config['IMPORTORG']['REGISTRY_API_BASEPATH']
import_org_name = config['IMPORTORG']['ORG']

def main():
    import_org_registry_api = import_org_registry_basepath + "apis/"
    import_org_domains_url = import_org_registry_basepath + "domains/"
    #Pull specs in the outgoing org
    org_specs_call = requests.get(import_org_registry_api + import_org_name, headers= {'Authorization': import_org_api_key, 'accept': 'application/json'})
    org_apis_json = org_specs_call.json()
    print(org_apis_json)
    if len(org_apis_json['apis']) == 0:
        raise RuntimeError("No APIs Found in Org- " + import_org_registry_api + import_org_name)
    
    
    print("Tearing down the " + import_org_name + " from " + import_org_registry_api)
    
    parse_org(org_apis_json, import_org_registry_api)
    
    org_domains_call = requests.get(import_org_domains_url + import_org_name, headers= {'Authorization': import_org_api_key, 'accept': 'application/json'})
    org_domains_json = org_domains_call.json()
    
    parse_org(org_domains_json, import_org_domains_url)
    
def parse_org(org_json, import_url):
    #parse api spec metadata from org call
    for metatdata in org_json["apis"]:
        
        url = metatdata["properties"][0]["url"] 
        last_slash = url.rindex('/', 0)
        formatted_url = url[0: last_slash]
        formatted_url = helper_functions.verify_http_type(formatted_url, import_url)
        
        sh_name = formatted_url[formatted_url.rindex('/', 0) + 1 : len(formatted_url)]
        
        delete_call= requests.delete(import_url + import_org_name +"/"+ sh_name, headers={'Authorization': import_org_api_key, 'accept': 'application/json'})
        
        if delete_call.status_code == 200:
            print("Successfully Deleted " + sh_name)
        else:
            print("Error has occurred")
            print(delete_call.text)
main()
    
    