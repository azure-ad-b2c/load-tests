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

