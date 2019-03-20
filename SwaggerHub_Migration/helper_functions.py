'''
Created on Mar 20, 2019

@author: Steven.Colon
'''
#Method to verify two urls using either HTTP or HTTPS (set by the basepath)
def verify_http_type(dynamic_url, basepath):
    if basepath.startswith("https") and not dynamic_url.startswith("https") :
        return dynamic_url.replace('http', 'https')
    else:
        return dynamic_url
    

