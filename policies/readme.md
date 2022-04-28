# Local account sign-in with rest api validation user journey overview

This article gives an overview of the **local account sign-in with rest api validation** user journey custom policy to be used for load testing sample. We recommend you to read the [Azure AD B2C custom policy overview](https://docs.microsoft.com/azure/active-directory-b2c/custom-policy-overview) before reading this article.


You can find the user journey and its orchestration steps in the TrustFrameworkBase.xml file, with the Id "SignUpOrSignIn". Each Orchestration step and its referenced technical profile will be explained in detail in the following series.

## Set Up

Replace tenant name in all policy files (replace yourtenant with corresponding tenant name).

Replace ProxyIdentityExperienceFrameworkAppId and IdentityExperienceFrameworkAppId with the corresponding values for your tenant.

To understand how to obtain these values please refer to the documentation [here](https://docs.microsoft.com/en-us/azure/active-directory-b2c/custom-policy-overview#prepare-your-environment).

## Logical Steps

For a user to be able to sign in, the following user experience must be translated into logical steps with a custom policy.

Handling Sign In:

1. Display a page where the user can enter their email and password.
1. If the user submits their credentials (signs in), we must validate the credentials.
1. Call a Web API to obtain the affiliate number and include this information in the token.
1. Display a page where the user can enter address and city (this is only for showing how to automated self-asserted steps in Load Testing tool)
1. Issue an id token.

## Translating this into custom policies  

Handling Sign In:

1. This requires a Self-Asserted technical profile. It must present output claims to obtain the email and password claims.
1. Use the combined sign in and sign up content definition, which provides this for us.
1. Run a Validation technical profile to validate the credentials.
1. Call a web api to obtain the affiliate number.
1. Call a self-asserted technical profile.
1. Call a technical profile to issue a token.  

## Building the custom policy

### Handling Sign In

**Orchestration Step 1**: Provides functionality for a user to sign up or sign in. This is achieved using a Self-Asserted technical profile and connected validation technical profile.

The XML required to generate this step is:

```xml
<OrchestrationStep Order="1" Type="CombinedSignInAndSignUp" ContentDefinitionReferenceId="api.signuporsignin">
  <ClaimsProviderSelections>
    <ClaimsProviderSelection ValidationClaimsExchangeId="LocalAccountSigninEmailExchange" />
  </ClaimsProviderSelections>
  <ClaimsExchanges>
    <ClaimsExchange Id="LocalAccountSigninEmailExchange" TechnicalProfileReferenceId="SelfAsserted-LocalAccountSignin-Email" />
  </ClaimsExchanges>
</OrchestrationStep>
```

The combined sign up and sign in page is treated uniquely by Azure AD B2C, since it presents a sign up link that can take the user to the sign up step.
This is achieved with the following two lines:

```xml
<OrchestrationStep Order="1" Type="CombinedSignInAndSignUp" ContentDefinitionReferenceId="api.signuporsignin">
```

Since Azure AD B2C understands that this is a sign in page, you must specify the `ClaimsProviderSelections` element with at least one reference to a `ClaimsProviderSelection`. This `ClaimsProviderSelection` maps to the `ClaimsExchange`, which ultimately calls a technical profile called `SelfAsserted-LocalAccountSignin-Email`.

The `SelfAsserted-LocalAccountSignin-Email` technical profile defines the actual page functionality:

```xml
<TechnicalProfile Id="SelfAsserted-LocalAccountSignin-Email">
  <DisplayName>Local Account Signin</DisplayName>
  <Protocol Name="Proprietary" Handler="Web.TPEngine.Providers.SelfAssertedAttributeProvider, Web.TPEngine, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null" />
  <Metadata>
    <Item Key="SignUpTarget">SignUpWithLogonEmailExchange</Item>
    <Item Key="setting.operatingMode">Email</Item>
    <Item Key="ContentDefinitionReferenceId">api.selfasserted</Item>
  </Metadata>
  <IncludeInSso>false</IncludeInSso>
  <InputClaims>
    <InputClaim ClaimTypeReferenceId="signInName" />
  </InputClaims>
  <OutputClaims>
    <OutputClaim ClaimTypeReferenceId="signInName" Required="true" />
    <OutputClaim ClaimTypeReferenceId="password" Required="true" />
    <OutputClaim ClaimTypeReferenceId="objectId" />
    <OutputClaim ClaimTypeReferenceId="authenticationSource" />
  </OutputClaims>
  <ValidationTechnicalProfiles>
    <ValidationTechnicalProfile ReferenceId="login-NonInteractive" />
  </ValidationTechnicalProfiles>
  <UseTechnicalProfileForSessionManagement ReferenceId="SM-AAD" />
</TechnicalProfile>
```

|Element name  |Description  |
|---------|---------|
|TechnicalProfile Id | Identifier for this technical profile. It is used to find the technical profile that this orchestration step calls.|
|DisplayName|Friendly name which can describe the function of this technical profile.|
|Protocol|The Azure AD B2C technical profile type. In this case, it is Self-Asserted, such that a page is rendered for the user to provide their inputs.|
|Metadata|For a Self-Asserted Combined Sign in and Sign up profile, we provide a SignUpTarget, which points to the Sign Up ClaimsExchange Id in a subsequent orchestrations step.|
|InputClaims|Enables the ability to pre-populate the signInName claim|
|OutputClaims| We require the user to provide their email and password, hence referenced as output claims. There are some claims here, such as objectId, that are not presented on the page since the validation technical profile satisfies this output claim.|
|ValidationTechnicalProfiles|The technical profile to launch to validate the date the user provided, in this case to validate their credentials.|
|UseTechnicalProfileForSessionManagement|References a technical profile to add this step into the session such that during SSO, this step is skipped.|

To see all the configuration options for a Self-Asserted technical profile, find more [here](https://docs.microsoft.com/azure/active-directory-b2c/self-asserted-technical-profile).

By calling this technical profile, we now satisfy the initial logical step for sign in. When the user submits the page, any validation technical profiles referenced by the technical profile will run. In this case, that is the validation technical profile `login-NonInteractive`.

`login-NonInteractive` is a technical profile, which makes an OpenId request using the [Resource Owner Password Credential](https://tools.ietf.org/html/rfc6749#section-4.3) grant flow to validate the users provided credentials at the Azure AD authorization server. This is an API-based login performed by the Azure AD B2C service against the Azure AD authentication service.

```xml
<TechnicalProfile Id="login-NonInteractive">
  <DisplayName>Local Account SignIn</DisplayName>
  <Protocol Name="OpenIdConnect" />
  <Metadata>
    <Item Key="UserMessageIfClaimsPrincipalDoesNotExist">We can't seem to find your account</Item>
    <Item Key="UserMessageIfInvalidPassword">Your password is incorrect</Item>
    <Item Key="UserMessageIfOldPasswordUsed">Looks like you used an old password</Item>

    <Item Key="ProviderName">https://sts.windows.net/</Item>
    <Item Key="METADATA">https://login.microsoftonline.com/{tenant}/.well-known/openid-configuration</Item>
    <Item Key="authorization_endpoint">https://login.microsoftonline.com/{tenant}/oauth2/token</Item>
    <Item Key="response_types">id_token</Item>
    <Item Key="response_mode">query</Item>
    <Item Key="scope">email openid</Item>

    <!-- Policy Engine Clients -->
    <Item Key="UsePolicyInRedirectUri">false</Item>
    <Item Key="HttpBinding">POST</Item>
  </Metadata>
  <InputClaims>
    <InputClaim ClaimTypeReferenceId="signInName" PartnerClaimType="username" Required="true" />
    <InputClaim ClaimTypeReferenceId="password" Required="true" />
    <InputClaim ClaimTypeReferenceId="grant_type" DefaultValue="password" AlwaysUseDefaultValue="true" />
    <InputClaim ClaimTypeReferenceId="scope" DefaultValue="openid" AlwaysUseDefaultValue="true" />
    <InputClaim ClaimTypeReferenceId="nca" PartnerClaimType="nca" DefaultValue="1" />
  </InputClaims>
  <OutputClaims>
    <OutputClaim ClaimTypeReferenceId="objectId" PartnerClaimType="oid" />
    <OutputClaim ClaimTypeReferenceId="tenantId" PartnerClaimType="tid" />
    <OutputClaim ClaimTypeReferenceId="givenName" PartnerClaimType="given_name" />
    <OutputClaim ClaimTypeReferenceId="surName" PartnerClaimType="family_name" />
    <OutputClaim ClaimTypeReferenceId="displayName" PartnerClaimType="name" />
    <OutputClaim ClaimTypeReferenceId="userPrincipalName" PartnerClaimType="upn" />
    <OutputClaim ClaimTypeReferenceId="authenticationSource" DefaultValue="localAccountAuthentication" />
  </OutputClaims>
</TechnicalProfile>
```

|Element name  |Description  |
|---------|---------|
|TechnicalProfile Id | Identifier for this technical profile. It is used to find the technical profile that this orchestration step calls.|
|DisplayName|Friendly name, which can describe the function of this technical profile.|
|Protocol|The Azure AD B2C technical profile type. In this case, it is OpenId, such that Azure AD B2C understands to make an OpenId request.|
|Metadata|Various configuration options to make a valid OpenId request since the grant_type is configured password and the HTTP binding is set to POST.  This also includes various error handling responses, such as incorrect password.|
|InputClaims|Passes the username and password into the POST body of the OpenId request.|
|OutputClaims| Maps the JWT issued by the authorization server into Azure AD B2C's claim bag. Here we obtain the objectId and authenticationSource, hence it is not shown on the Self-Asserted page.|

To see all the configuration options for an OpenID technical profile, find more [here](https://docs.microsoft.com/en-us/azure/active-directory-b2c/openid-connect-technical-profile).

We have now rendered a sign in page to the user, allowed the user to enter their email and password, and finally validated their credentials.

**Orchestration Step 2** - Read any additional data from the user object.

We maybe storing additional data the user provided or other data on the user object, which allows your application/service to function correctly.

Therefore, we will read the user object for any desired attributes to add into the Azure AD B2C claims bag.

The following Orchestration step calls a technical profile called `AAD-UserReadUsingObjectId`, which provides this functionality.
The ClaimsExchange Id is unique name for this claims exchange that you can set.

```xml
<OrchestrationStep Order="3" Type="ClaimsExchange">
  <ClaimsExchanges>
    <ClaimsExchange Id="AADUserReadWithObjectId" TechnicalProfileReferenceId="AAD-UserReadUsingObjectId" />
  </ClaimsExchanges>
</OrchestrationStep>
```

The referenced technical profile is as follows:

```xml
<TechnicalProfile Id="AAD-UserReadUsingObjectId">
  <Metadata>
    <Item Key="Operation">Read</Item>
    <Item Key="RaiseErrorIfClaimsPrincipalDoesNotExist">true</Item>
  </Metadata>
  <IncludeInSso>false</IncludeInSso>
  <InputClaims>
    <InputClaim ClaimTypeReferenceId="objectId" Required="true" />
  </InputClaims>
  <OutputClaims>
    <OutputClaim ClaimTypeReferenceId="signInNames.emailAddress" />
    <OutputClaim ClaimTypeReferenceId="displayName" />
    <OutputClaim ClaimTypeReferenceId="otherMails" />
    <OutputClaim ClaimTypeReferenceId="givenName" />
    <OutputClaim ClaimTypeReferenceId="surname" />
  </OutputClaims>
  <IncludeTechnicalProfile ReferenceId="AAD-Common" />
</TechnicalProfile>
```

This technical profile does not state a protocol, therefore is automatically of type `Azure Active Directory`, which provides the ability to read or write to the directory structure.


|Element name  |Description  |
|---------|---------|
|TechnicalProfile Id|Identifier for this technical profile. It is used to find the technical profile that this orchestration step calls.|
|Metadata|This is configured to read the directory. And to throw an error if the user is not found.|
|InputClaims|This is asking to lookup any matching user account in the directory with the objectId from the Azure AD B2C claims bag. This objectId will have been received via the `login-NonInteractive` technical profile and output into the claims bag by the `SelfAsserted-LocalAccountSignin-Email` technical profile. |
|OutputClaims|We are asking to read these claims from the directory. The Azure AD B2C claims referenced here have the same name as the attribute name in the directory. |
|IncludeTechnicalProfile|AAD-Common is included to provide the foundational functionality to read or write to the directory.|

A special case must be noted for the `signInNames.emailAddress`, this references the attribute `signInNames` which is a collection of key value pairs. In this case, we are reading back the `emailAddress` key within the `signInNames` attribute.


**Orchestration Step 3** - Calls a Web API.

This step was added for testing purposes only and to show a way to monitor the api response time using App Insights.

```xml
<OrchestrationStep Order="3" Type="ClaimsExchange">
  <ClaimsExchanges>
    <ClaimsExchange Id="WebAPIGet" TechnicalProfileReferenceId="WebAPIGet" />
  </ClaimsExchanges>
</OrchestrationStep>  
```

The referenced technical profile is as follows:


```xml
<TechnicalProfile Id="WebAPIGet">
  <DisplayName>Test Web API Get method</DisplayName>
  <Protocol Name="Proprietary" Handler="Web.TPEngine.Providers.RestfulProvider, Web.TPEngine, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null" />
  <Metadata>
    <Item Key="ServiceUrl">[Replace with Web API URL]</Item>
    <Item Key="AuthenticationType">None</Item>
    <Item Key="AllowInsecureAuthInProduction">true</Item>
    <Item Key="SendClaimsIn">QueryString</Item>
    <Item Key="IncludeClaimResolvingInClaimsHandling">true</Item>          
    <Item Key="DefaultUserMessageIfRequestFailed">Cannot process your request right now, please try again later.</Item>
  </Metadata>
  <InputClaimsTransformations>
    <InputClaimsTransformation ReferenceId="GetPreApiCallDateTime" />
  </InputClaimsTransformations>
  <InputClaims>
    <InputClaim ClaimTypeReferenceId="signInNames.emailAddress" PartnerClaimType="email" />
  </InputClaims>
  <OutputClaims>             
    <OutputClaim ClaimTypeReferenceId="affiliateNumber" />        
  </OutputClaims>
  <OutputClaimsTransformations>
    <OutputClaimsTransformation ReferenceId="GetPostApiCallDateTime" />
  </OutputClaimsTransformations>          
</TechnicalProfile>
```

Please replace the ServiceUrl value with the corresponding Url of the Web Api being called for testing.

In this Technical Profile 2 Claims Transformations are being used to obtain the datetime before and after the call to the Web Api, to later be reported to App Insights.

```xml
<ClaimsTransformation Id="GetPreApiCallDateTime" TransformationMethod="GetCurrentDateTime">
  <OutputClaims>
      <OutputClaim ClaimTypeReferenceId="preApiCall" TransformationClaimType="currentDateTime" />
  </OutputClaims>
</ClaimsTransformation>            
<ClaimsTransformation Id="GetPostApiCallDateTime" TransformationMethod="GetCurrentDateTime">
  <OutputClaims>
      <OutputClaim ClaimTypeReferenceId="postApiCall" TransformationClaimType="currentDateTime" />
  </OutputClaims>
</ClaimsTransformation>
```

This transformations obtain the current datetime and stores it in a claim.


**Orchestration Step 4** - Register telemetry information in App Insights.

This step was added just to demonstrate how to generate telemetry in App Insights:

```xml
<OrchestrationStep Order="4" Type="ClaimsExchange">
  <ClaimsExchanges>
    <ClaimsExchange Id="TrackWebApiTime" TechnicalProfileReferenceId="AppInsights-TrackWebApiTime" />
  </ClaimsExchanges>
</OrchestrationStep>   
```

To understand how to integrate custom policies with App Insights for telemetry read the documentation [here](https://docs.microsoft.com/en-us/azure/active-directory-b2c/analytics-with-application-insights?pivots=b2c-custom-policy).

The referenced technical profile is as follows:

```xml
<TechnicalProfile Id="AppInsights-TrackWebApiTime">
  <InputClaims>
    <InputClaim ClaimTypeReferenceId="EventType" PartnerClaimType="eventName" DefaultValue="WebApiCalled" />
    <InputClaim ClaimTypeReferenceId="preApiCall" PartnerClaimType="{property:preApiCall}" />
    <InputClaim ClaimTypeReferenceId="postApiCall" PartnerClaimType="{property:postApiCall}" />
    <InputClaim ClaimTypeReferenceId="correlationId" PartnerClaimType="{property:correlationId}" />
    <InputClaim ClaimTypeReferenceId="signInNames.emailAddress" PartnerClaimType="{property:signInNames.emailAddress}" />
  </InputClaims>
  <IncludeTechnicalProfile ReferenceId="AppInsights-Common" />
</TechnicalProfile>      
```
Notice that preApiCall, postApiCall and correlationId are added for evaluation purposes.


**Orchestration Step 5** - Issue an id token.

In most user journeys, the journey will end by issuing an id token back to the application. This orchestration step looks as follows:

```xml
<OrchestrationStep Order="5" Type="SendClaims" CpimIssuerTechnicalProfileReferenceId="JwtIssuer" />
```

The referenced technical profile is as follows:

```xml
<TechnicalProfile Id="JwtIssuer">
  <DisplayName>JWT Issuer</DisplayName>
  <Protocol Name="None" />
  <OutputTokenFormat>JWT</OutputTokenFormat>
  <Metadata>
    <Item Key="client_id">{service:te}</Item>
    <Item Key="issuer_refresh_token_user_identity_claim_type">objectId</Item>
    <Item Key="SendTokenResponseBodyWithJsonNumbers">true</Item>
  </Metadata>
  <CryptographicKeys>
    <Key Id="issuer_secret" StorageReferenceId="B2C_1A_TokenSigningKeyContainer" />
    <Key Id="issuer_refresh_token_key" StorageReferenceId="B2C_1A_TokenEncryptionKeyContainer" />
  </CryptographicKeys>
  <InputClaims />
  <OutputClaims />
</TechnicalProfile>
```

This step does not need configuring any further, but find out more [here](https://docs.microsoft.com/en-us/azure/active-directory-b2c/jwt-issuer-technical-profile).

## Summary

The set of steps implemented in this policy are to demonstrate how to implement a Load Test using Azure Load Testing Service.


