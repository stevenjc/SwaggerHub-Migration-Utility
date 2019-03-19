'''
Created on Mar 19, 2019

@author: Steven.Colon
'''


#IMPORTANT NOTE - THIS SCRIPT WILL DELETE EVERY SPEC IN A ORG
import requests
import json

input("WARNING - This Script will delete all API specs from a SwaggerHub Org. Press Enter to continue ...")
with open('../config.json', 'r') as file:
    config = json.load(file)
    
onprem_api_key= config['ONPREM']['API_KEY']
onprem_registry_api = config['ONPREM']['REGISTRY_API_BASEPATH']
onprem_org = config['ONPREM']['ORG']

#Pull specs in the outgoing org
org_specs_call = requests.get(onprem_registry_api + onprem_org, headers= {'Authorization': onprem_api_key, 'accept': 'application/json'})
org_specs = org_specs_call.json()

if len(org_specs['apis']) == 0:
    print("ERROR No APIs Found")
    exit()


print("Tearing down the " + onprem_org + " from SwaggerHub OnPrem installation")

#parse api spec metadata from org call
for api_metadata in org_specs["apis"]:
    
    api_url = api_metadata["properties"][0]["url"] 
    last_slash = api_url.rindex('/', 0)
    formatted_api_url = api_url[0: last_slash]

    api_sh_name = formatted_api_url[formatted_api_url.rindex('/', 0) + 1 : len(formatted_api_url)]
    
    api_delete_call= requests.delete(onprem_registry_api + onprem_org +"/"+ api_sh_name, headers={'Authorization': onprem_api_key, 'accept': 'application/json'})
    
    if api_delete_call.status_code == 200:
        print("Successfully Deleted " + api_sh_name)
    else:
        print("Error has occurred")
        print(api_delete_call.text)

    