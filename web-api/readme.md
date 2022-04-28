# Web APi overview

This article gives an overview of the **Web API** included for testing purposes in the sample. This is implemented as a Node.js Azure Function. 

The documentation to understand how to create an Azure Function and deploy the sample can be found [here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-node).


## Behavior

This is a simple web api that receives an email and generates an affiliate number (random) for testing purposes.

```javascript
module.exports = async function (context, req) {
    context.log('JavaScript HTTP trigger function processed a request.');

    //this lines generates a random affiliate number for testing purposes
    const email = (req.query.email || (req.body && req.body.email));
    const min = 1;
    const max = 1000;
    const affiliateNumber = Math.floor(Math.random() * (max - min) + min);

    //this lines simulate a delay in execution of the api 
    // const stop = new Date().getTime() + 1000;
    // while(new Date().getTime() < stop);  

    var jsonResult = {
        "version": "1.0.0",
        "status": 200,
        "affiliateNumber": affiliateNumber
        }

    context.res = {
        status: 200, 
        body: jsonResult
    };
}
```

The code commented in line 22 allows to simulate a delay in the execution for testing purposes.

It will always return a HTTP 200 Status.

