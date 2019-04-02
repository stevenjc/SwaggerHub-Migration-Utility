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
migrate_team_roles = config ['EXPORTORG']['MIGRATE_TEAM_ROLES']

if not type(migrate_team_roles) is bool:
    raise TypeError("MIGRATE_TEAM_ROLES needs to be a boolean value")

import_org_api_key= config['IMPORTORG']['API_KEY']
import_org_registry_basepath = config['IMPORTORG']['REGISTRY_API_BASEPATH']
import_org_name = config['IMPORTORG']['ORG']
private_visibility = config['IMPORTORG']['DEFAULT_PRIVATE_VISIBILITY']

#check for boolean type in config
if not type(private_visibility) is bool:
    raise TypeError("DEFAULT_PRIVATE_VISIBILITY needs to be a boolean value")

def main():
    #URL to pull/push API Specs
    export_org_registry_api = export_org_registry_basepath +"apis/"
    import_org_registry_api = import_org_registry_basepath + "apis/"
        
    #Pull specs in the outgoing org
    org_specs_call = requests.get(export_org_registry_api + export_org_name, headers= {'Authorization': export_org_api_key})
    org_apis_json = org_specs_call.json()
    
    if len(org_apis_json['apis']) == 0:
        raise RuntimeError("No APIs Found in Import Org")
    
    print("Migrating " + str(org_apis_json["totalCount"]) + " OAS Specs from " + export_org_registry_api + export_org_name + " to " + import_org_registry_api + import_org_name)
    
    parse_org(org_apis_json, export_org_registry_api, import_org_registry_api, True)
    
    export_org_domains_url = export_org_registry_basepath + "domains/"
    import_org_domains_url = import_org_registry_basepath + "domains/"
    
    export_org_domains_call = requests.get(export_org_domains_url + export_org_name, headers= {'Authorization': export_org_api_key})
    
    export_org_domains_json = export_org_domains_call.json()
    
    print("Migrating " + str(export_org_domains_json["totalCount"]) + " Domains from " + export_org_registry_api + export_org_name + " to " + import_org_registry_api + import_org_name +"\n\n")
    
    parse_org(export_org_domains_json, export_org_domains_url,import_org_domains_url, False)
    


def parse_org(org_json, export_url, import_url, migrating_apis):
    for metadata in org_json["apis"]:
        info = pull_url_and_name(metadata, export_url)
        formatted_url = info["url"]
        sh_name = info["name"]
        
        #Pull json that shows each version of the spec 
        versions_call= requests.get(formatted_url, headers={'Authorization': export_org_api_key})
        versions_json = versions_call.json()
    
        print("Found " + str(versions_json["totalCount"]) + " versions ...")
        
        export_versions(versions_json, sh_name, export_url, import_url)
        
        #Check if running API Spec migration and 
        if migrating_apis and migrate_team_roles:
            collab_json = pull_team_and_roles(formatted_url)
            if len(collab_json['teams']) != 0:
                print("Teams Found")
                teams_payload = construct_teams_payload(collab_json)
                import_teams(import_url + import_org_name + "/" + sh_name , teams_payload)
            else:
                print("No Teams Found to Migrate")
            
            

#Format URL of API or Domain and retrieve Name in SwaggerHub
def pull_url_and_name(metadata, export_url):
    #Remove Default Version number from API Url so that we can pull all versions
    url = metadata["properties"][0]["url"] 
    last_slash = url.rindex('/', 0)
    formatted_url = url[0: last_slash]
    formatted_url = helper_functions.verify_http_type(formatted_url, export_url)
    
    #Pull name of spec in SwaggerHub (different from the real name of the spec)
    sh_name = formatted_url[formatted_url.rindex('/', 0) + 1 : len(formatted_url)]
    
    return {"url": formatted_url, "name": sh_name}
        
def export_versions(versions_json, sh_name, export_url, import_url):
    #Pull API Version URLs
    for version in versions_json['apis']:
        api_version_url = helper_functions.verify_http_type(version["properties"][0]["url"], export_url)
        print(api_version_url)
        version_number = version["properties"][1]["value"]
        #Get spec of single API Version
        api_version_spec_call = requests.get(api_version_url, headers = {'Authorization': export_org_api_key})
        
        #push spec to OnPrem 
        import_org_post_url = import_url + import_org_name + "/" + sh_name + '?isPrivate=' + str(private_visibility) + '&version=' + version_number
        
        api_version_spec_json = api_version_spec_call.json()
        
        print("Posting Spec to - " + import_org_post_url)
        
        import_version(import_org_post_url, api_version_spec_json)
            
    print("\n")
        
        
def import_version(import_org_post_url, api_version_spec_json):
    onprem_post_call = requests.post(import_org_post_url, headers={'Authorization': import_org_api_key}, json=api_version_spec_json)
        
    if(onprem_post_call.status_code != 201 and onprem_post_call.status_code != 200):
        raise RuntimeError("Invalid OnPrem API Response - " + onprem_post_call.text)
    
def pull_team_and_roles(url):
    print("getting collab for " + url)
    collab_get_call = requests.get(url + "/.collaboration", headers = {'Authorization': export_org_api_key})
    
    collab_json = collab_get_call.json()
    print(collab_json)
    return collab_json

#Creates payload for all teams with only name and roles
def construct_teams_payload(collab_json):
    team_counter = 0 #counter to track teams to correctly add commas
    collab_team_info = '{"teams":['
    for team in collab_json["teams"]:
        if team_counter != 0: #add comma before every team except first one
            collab_team_info += ","
        collab_team_info += '{"name":"%s","roles":%s}'%(team['name'],str(team['roles']).replace("'", '"'))
        team_counter += 1
    collab_team_info += ']}'
    print(collab_team_info)
    return collab_team_info
    

def import_teams(url, payload):
    print(url + "/.collaboration")
    import_teams_call = requests.put(url + "/.collaboration", headers={'Authorization': import_org_api_key}, json = json.loads(payload))
    
    if(import_teams_call.status_code != 201 and import_teams_call.status_code != 200):
        raise RuntimeError("Invalid OnPrem API Response - " + import_teams_call.text)
     
main()

    


        

