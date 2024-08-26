
# Auth Steps

## Creation

 1. Person Create RSA Private/Public Keys
 2. Person Create User
    - Pass PubKey, Username as parameters
 3. Server
    - Generate AccessKeyId
    - Store AccessKeyID, PubKey
 4. Server Reply with AccessKeyID



```mermaid
---
title: AccessKey / User Creation Diagram
---
flowchart LR
    U{Admin\nStart}
    p([RSA Public Key])
    P([RSA Private Key])
    0[API Call - Create User]
    u([Username])
    1(Server)
    a([AccessKeyID])
    2(AuthDB)

    0== pass ==>p
    U-. 2 - call .->0
    U-. 1 - create .->p
    0== pass ==>u
    a== store ==>2
    a== reply ==>U
    1== generate ==>a
    u== send ==>1
    p== store ==>2
    p== send ==>1
    U-. 1 - create .->P

```


## Authorization

 1. Person Authorize
    - Pass AccessKeyID as parameter
    - Client/API Requires PrivKey; Is **NOT** passed to Server
 2. Server
    - Check for valid AccessKeyID
    - Generate AuthToken
    - Using PubKey in AuthDB paired with AccessKeyID, Encrypt AuthToken
    - Send Encrypted AuthToken to Client/API
 3. Client/API Validate
    - Using PrivKey, Attempt decryption of Encrypted AuthToken
    - Send Decrypted AuthToken back to Server as Verification
 4. Server
    - Check for valid AccessKeyID
    - Check that AuthToken is valid (exists in AuthDB, not expired)
 5. Client/API Token Display
    - Provide Token to Person


```mermaid
---
title: Authorization Prompt/Response
---
flowchart LR
    U{Start}
    P([RSA Private Key])
    p([RSA Public Key])
    b([AccessKeyID])
    1[API Call - Authorize]
    2(Server)
    T([AuthToken])
    t{{AuthToken}}
    3(Response)
    c[Response with Token]

    U-. 1 - call .->1
    b== send ==>2
    1== pass ==>b
    1== load ==>P
    2== load ==>p
    3== reply ==>c
    T== output ==>3
    p-- encrypts -->T
    c-- decrypted by ---P
    P-- derives -->t
    U-. 2 - utilize .->t
```

## Commands

 1. Person Command
    - Pass AccessKeyId as Parameter
    - Pass AuthToken as Parameter
 2. Server
    - Check for valid AccessKeyID
    - Check that AuthToken is valid (exists in AuthDB, not expired)
    - Check for UACL, GACL Allowance
 3. Server Command Processing
 4. Response

```mermaid
---
title: Authorization Prompt/Response
---
flowchart LR
    U{Start}
    1[API Call - $COMMAND]
    b([AccessKeyID])
    t{{AuthToken}}
    2(Server)
    Z[[User ACL]]
    X[[Group ACL]]
    Y{{User}}


    2-. check valid .->b
    2-. check valid .->t
    1== pass ==>b
    1== pass ==>t
    U-. 1 - call .->1
    Z-- checks --->Y
    X-- checks --->Y
    Z== notifies ==>2
    X== notifies ==>2
    b== send ==>2
    t== derives ==>Y
    b== derives ==>Y
    t== send ==>2
```