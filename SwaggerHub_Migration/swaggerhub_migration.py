'''
Created on Mar 19, 2019

@author: Steven.Colon
'''
import requests
import json

with open('config.json', 'r') as file:
    config = json.load(file)

saas_api_key= config['SAAS']['API_KEY']
saas_registry_api = config['SAAS']['REGISTRY_API_BASEPATH']
saas_org = config['SAAS']['ORG']

onprem_api_key= config['ONPREM']['API_KEY']
onprem_registry_api = config['ONPREM']['REGISTRY_API_BASEPATH']
onprem_org = config['ONPREM']['ORG']

#Pull specs in the outgoing org
org_specs = requests.get(saas_registry_api + saas_org, headers= {'Authorization': saas_api_key, 'accept': 'application/json'}).json()

print("Migrating " + str(org_specs["totalCount"]) + " OAS Specs... \n")

#parse api spec metadata from org call
for api_metadata in org_specs["apis"]:
#    print(str(api_spec) + "\n\n\n\n\n\n")
    api_url = api_metadata["properties"][0]["url"] 
    last_slash = api_url.rindex('/', 0)
    formatted_api_url = api_url[0: last_slash]

    api_sh_name = formatted_api_url[formatted_api_url.rindex('/', 0) + 1 : len(formatted_api_url)]
    print("Name - " + api_sh_name)
    print("Pulling versions from " + formatted_api_url)

    #pull each version of the spec 
    api_versions= requests.get(formatted_api_url, headers={'Authorization': saas_api_key, 'accept': 'application/json'}).json()

    print("Found " + str(api_versions["totalCount"]) + " versions ...")
    #Pull API Version URLs
    for api_version in api_versions['apis']:
        api_version_url = api_version["properties"][0]["url"]
        print(api_version_url)
        #Get spec of single API Version
        api_version_spec_call = requests.get(api_version_url, headers = {'Authorization': saas_api_key, 'accept': 'application/json'})
        #print("Status of API Version Spec Call - " +  str(api_version_spec_call.status_code))
        
        #push spec to OnPrem 
        onprem_post_url = onprem_registry_api + onprem_org + '/' + api_sh_name + '?isPrivate=true&force=true'
        
        #print("Posting Spec to - " + onprem_post_url)
        
        onprem_post_call = requests.post(onprem_post_url, headers={'Authorization':onprem_api_key}, json=api_version_spec_call.json())
        
        if(onprem_post_call.status_code != 201 and onprem_post_call.status_code != 200):
            print('INVALID ONPREM POST RESPONSE')
            exit()
        else:
            print("API Version Uploaded to OnPrem")
            
    print("\n")




        

