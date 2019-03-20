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
import_org_registry_api = config['IMPORTORG']['REGISTRY_API_BASEPATH']
import_org_name = config['IMPORTORG']['ORG']

#Pull specs in the outgoing org
org_specs_call = requests.get(import_org_registry_api + import_org_name, headers= {'Authorization': import_org_api_key, 'accept': 'application/json'})
org_specs_json = org_specs_call.json()

if len(org_specs_json['apis']) == 0:
    raise RuntimeError("No APIs Found in Org- " + import_org_registry_api + import_org_name)


print("Tearing down the " + import_org_name + " from " + import_org_registry_api)

#parse api spec metadata from org call
for api_metadata in org_specs_json["apis"]:
    
    api_url = api_metadata["properties"][0]["url"] 
    last_slash = api_url.rindex('/', 0)
    formatted_api_url = api_url[0: last_slash]
    formatted_api_url = helper_functions.verify_http_type(formatted_api_url, import_org_registry_api)
    
    api_sh_name = formatted_api_url[formatted_api_url.rindex('/', 0) + 1 : len(formatted_api_url)]
    
    api_delete_call= requests.delete(import_org_registry_api + import_org_name +"/"+ api_sh_name, headers={'Authorization': import_org_api_key, 'accept': 'application/json'})
    
    if api_delete_call.status_code == 200:
        print("Successfully Deleted " + api_sh_name)
    else:
        print("Error has occurred")
        print(api_delete_call.text)

    
    