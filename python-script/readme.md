# Python Script Overview

This article gives an overview of the **Python Script** included for bulk creating users for Load Testing. 

This scrips uses a .csv file as a source of information. The same file will be used by the Load Testing Script later for execution so it must be the same for both creation of users and execution of the Load Test.

## Requirements

For editing and running the script you will need to install the following:

1. Visual Studio Code ([Download link here](https://code.visualstudio.com/))
1. Python 3.6 or above (Install from Microsoft Store is recommended as it contains PIP package manager)
1. Python extensions for VS Code 

The detailed documentation on how to install and run a Python script can be found [here](https://docs.microsoft.com/en-us/windows/python/scripting)

## Set up Python dev environment

1. Install VS Code 
1. Install Python from Microsoft Store (3.6 or above)
1. Install Python extension for VS Code
1. Open the load-testing folder in VS Code
1. Open a Command prompt terminal and navigate to the "script" folder (where the python script resides)
1. Create a virtual environment by executing this command: "python -m venv .venv"
1. Activate the virtual environment by executing this command: ".\\.venv\Scripts\activate.bat" 
1. Open VS Code inside the Virtual environment by executing this command: "code ." in the same terminal window
1. Verify that you are running in the venv by checking the Python interpreter in the low right corner of VS Code (should include the name of the virtual environment - in this case is .venv)
1. Close the initial VS Code instance and work in the new instantiated one (to use the venv)
1. Open a new terminal in the new VS Code Instance
1. Install dependencies by running "pip install -r requirements.txt" from the "script" folder
1. Run the script by hitting F5 or the "Run" menu, and then select "Python File: debug the currently active python file".

## App registration in B2C

To run the script an application must be registered in B2C and an application secret must be configured. This information will be used by the script to connect to B2C to obtain an access token to later call the Graph API for user creation.

The documentation to understand how to register an application in Azure AD B2C can be found [here](https://docs.microsoft.com/en-us/azure/active-directory-b2c/tutorial-register-applications?tabs=app-reg-ga).

Replace the Client Id, Client Secret and tenant name in the script.
 
The file Users.csv needs to be modified so the users email is the same as the tenant being tested (replace yourtenant with the tenant name).

## Behavior

The script will obtain an access token using the client id and client secret, then will load the CSV and start calling the Graph API to create the users.

```Python
import csv 
import json 
import msal 
import requests
from datetime import datetime


def csv_to_b2c(csvFilePath):

    clientId = "[Replace with the Client Id of the registered App]"
    clientSecret = "[Replace with the Client Secret corresponding to the App Id]"
    authority = "https://login.microsoftonline.com/yourtenant.onmicrosoft.com/"
    scope = "https://graph.microsoft.com/.default"
    token = ""
    graphCreatUserEndpoint = "https://graph.microsoft.com/v1.0/users"

    #create a confidential app instance to obtain a token.
    app = msal.ConfidentialClientApplication(
        clientId, 
        authority=authority,
        client_credential=clientSecret
        )

    result = app.acquire_token_for_client(scopes=scope)

    if "access_token" in result:
        token = result['access_token']

        #read csv file
        with open(csvFilePath, encoding='utf-8') as csvf: 
            #load csv file data using csv library's dictionary reader
            csvReader = csv.DictReader(csvf) 

            #convert each csv row into python dict
            for i, row in enumerate(csvReader): 

                rowNum = i+1

                newUser = {
                    "accountEnabled": True,
                    "displayName": row['displayname'],      
                    "surname": row['surname'],             
                    "givenName": row['givenname'],
                    "userPrincipalName": row['upn'],
                    "mailNickname": row['givenname'],
                    "passwordPolicies": "DisablePasswordExpiration",
                    "passwordProfile": {
                        "password": row['password'],
                        "forceChangePasswordNextSignIn": False                  
                        }
                    }
                
                # Calling graph using the access token
                response = requests.post( 
                    graphCreatUserEndpoint,
                    headers={'Authorization': 'Bearer ' + token,'Content-Type': 'application/json'},
                    data=json.dumps(newUser)
                    ).json()

                print("Graph API call result: %s" % json.dumps(response, indent=2))    


    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))  # You may need this when reporting a bug    

    
print("\nStarting CSV to B2C:\n\t")
startDate = datetime.now()
csvFilePath = r'Users.csv'
csv_to_b2c(csvFilePath)
endDate = datetime.now()
tookTime = (endDate-startDate).total_seconds()
print("\nFinished CSV to B2C - took " + str(tookTime) + " seconds")
```
