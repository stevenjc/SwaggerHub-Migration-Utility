# SwaggerHub-Installation-Migration-Utility

SwaggerHub-Installation-Migration-Utility is a migration utility for current SwaggerHub users to move their API Specs and domains to another SwaggerHub Organization. 

The other organization can be in a different installation of SwaggerHub. So you can migrate from SmartBears cloud hosted to OnPrem or between OnPrem installations. 

## Important Note 

Created by Steven Colon. 

This script is not supported by SmartBear Software Inc.

## Install Instructions 

Made on Python 3.7.1

Requires the requests python library - http://docs.python-requests.org/en/master/ 

## Execution Instructions

1. Download Repo locally

2. Create 'config.json' in same directory as swaggerhub_migration.py and enter SwaggerHub information as shown here
Note- You can pull the API Key from User Account Settings: https://app.swaggerhub.com/help/account/settings 

3. Execute script - python swaggerhub_migration.py


## License

   Copyright 2019 Steven Colon

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.



