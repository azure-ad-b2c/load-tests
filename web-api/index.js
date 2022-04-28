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