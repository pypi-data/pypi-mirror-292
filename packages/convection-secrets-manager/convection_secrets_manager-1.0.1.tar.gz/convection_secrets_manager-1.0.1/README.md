# Convection Secrets Manager

- [Convection Secrets Manager](#convection-secrets-manager)
  - [About](#about)
    - [How does it work?](#how-does-it-work)
  - [Usage](#usage)
    - [Commands and API](#commands-and-api)
  - [Configuration](#configuration)
  - [Automated Setup](#automated-setup)
    - [Questions requiring Root](#questions-requiring-root)
    - [Notes](#notes)
  - [Manual Setup](#manual-setup)
    - [Manual Setup Steps](#manual-setup-steps)
    - [Manual Installation](#manual-installation)
    - [Configure the Server](#configure-the-server)
      - [Notes](#notes-1)
    - [Initialization](#initialization)
    - [Configure the Client](#configure-the-client)
        - [Configuration File](#configuration-file)
        - [AuthFile File](#authfile-file)
      - [Client Configuration](#client-configuration)
      - [AuthFile Configuration](#authfile-configuration)
  - [Operational Notes](#operational-notes)
    - [Key Rotation](#key-rotation)
      - [Root Key / Unlock Key Rotation `rotate_root_keys`](#root-key--unlock-key-rotation-rotate_root_keys)
      - [KeySet Rotation `rotate_keyset`](#keyset-rotation-rotate_keyset)
    - [User / Group Management](#user--group-management)
  - [Internals](#internals)
    - [Unlock Keys](#unlock-keys)
      - [Rotation](#rotation)
      - [Revocation](#revocation)
    - [Locking / Unlocking](#locking--unlocking)
    - [The KeyDB](#the-keydb)
      - [Root Key](#root-key)
      - [KeyMapDB](#keymapdb)
      - [AuthDB](#authdb)
      - [KeySets](#keysets)
    - [Access Key Pairs](#access-key-pairs)
    - [Secret Storage](#secret-storage)
      - [Plugins](#plugins)
        - [Plugin Types](#plugin-types)
    - [Communication](#communication)
      - [Request Objects](#request-objects)
      - [Response Object](#response-object)
      - [Local Socket](#local-socket)
      - [Networking](#networking)
        - [Network ACLs (NACL)](#network-acls-nacl)
        - [Minimal NACLs](#minimal-nacls)
      - [WebSocket](#websocket)
    - [Groups](#groups)
    - [Users](#users)
      - [Access Tokens](#access-tokens)
    - [User / Group ACLs](#user--group-acls)
      - [ACL Type - Generic (`ACLObject`)](#acl-type---generic-aclobject)
      - [ACL Type - Command (`ACLCommand`)](#acl-type---command-aclcommand)
      - [ACL Type - Store (`ACLStore`)](#acl-type---store-aclstore)
  - [Extra Notes](#extra-notes)

## About

Convection Secrets Manager is a Secrets Storage Server and Client, capable of storing many different types of data. This is part of the Convection Suite of tools.

This package provides the Server and Server Console only. [Client can be found here](https://gitlab.com/accidentallythecable-public/convection-suite/convection-secrets-client)

### How does it work?

Convection Secrets Manager uses [Fernet](https://nceca.in/2021/52FERNET_System.pdf) via `cryptography.Fernet` in order to encrypt/decrypt data. Upon initialization, a set of [Unlock Keys](#unlock-keys) are generated, along with a [KeyDB](#the-keydb) for each key. At startup, the [KeyDB(s)](#the-keydb) are [locked](#locking--unlocking), and one of the [Unlock Keys](#unlock-keys) must be sent in order for the Secrets Manager in order to function. Once [unlocked](#locking--unlocking), a user can obtain a (time limited) token in order to access encrypted data and manage the server. [Users](#users) authorize themselves with an [Access Key Pair](#access-key-pairs) in order to obtain a token. Communication between the Server and Client are done via Secure Sockets using TLS 1.3+. This configured on the local unix socket as well. If used with networking enabled, [Network ACLs](#network-acls-nacl) are also used to limit access. Secrets are stored in (one or) many files, with the contents of each file (when decrypted) being dependent on the type of data being stored.

## Usage

The Convection Secrets Manager client provides both a CLI as well as a Semi-API library. The server provides a secure `AF_UNIX` socket for local communication and, optionally a secure `AF_INET` socket for remote communication as well as a secure `WebSocket` for WebUI operations

### Commands and API

Convection Secrets Manager comes with console (CLI) access, as well as a Semi-API library.

Information about CLI Commands or the API / Client Library can be found [here](API.md)

## Configuration

See [CONFIG.md](CONFIG.md)

## Automated Setup

Convection Secrets Manager comes with a setup utility in order to quickly get running. This can be accessed using `convection-secrets-setup`. It will very likely need to be run as root, depending on the answers to some of the questions.

In order to save time, an Answer File can be created, which can be passed to the setup command via the `--data` argument. Any questions not answered in the answer file will be asked before proceeding. If you wish to use the default (the value in `[]` brackets), simply press enter to continue to the next question. To additionally help with creating an Answer File in the future, the Answers provided are printed to the console so that they can be saved as an answer file for later.

Answer Files can be JSON, YAML or TOML. The type will automatically be picked up from the file extension, or you can use the `--input-type` argument to force specify a type.

### Questions requiring Root

Depending on the answer to these questions, root will be required in order to perform the neccessary action(s)

 - Create Server User/Group
 - PID Dir
 - Server Log File Path
 - Server Configuration Directory
 - Secrets Directory
 - Socket Path
 - Generate TLS Certificate
 - Listen Port, *if less than 1024; default is 9670*
 - WebSocket Port, *if less than 1024; default is 9671*
 - Install as Service

### Notes

 - This process does not create an AuthFile, you will need to do that by hand, if you wish to use one.
 - NACLs are not created as part of the setup process. You will need to configure these yourself
 - **Because the chance for most users to use /var/run (or some other standardized run directory), the installer does not modify permissions of the PID Dir. The service may be unable to start as a result. Ensure that the user running Convection Secrets Manager can create files in the PID Dir, Socket Path, and Log File Path.**

## Manual Setup

### Manual Setup Steps

 1. Install Convection Secrets Manager
 2. Configure the Server
 3. Create an RSA Public/Private Keypair
 4. Initialize the Server
 5. (Optional) Create an AuthFile
 6. (Optional) Create a Recovery User
 7. Setup Groups
 8. Setup ACLs
 9. Setup Users
 10. Create Client Configuration
 11. Create Secrets
 12. Manage your secrets!

### Manual Installation

Depending on installation choice, additional steps might have to be completed manually.

 1. (Optional, Recommended) Create a user such as `convection_sm`
    - Do not use `/home/` for the users home directory
    - Do not use `$SECRET_STORE` for the users home directory
    - Do not allow this user to have shell access (set shell to `/sbin/nologin`)
 2. Create a directory to store the server config files in one of these directories:
    - `/etc/convection-secrets/`
    - `$HOME_OF_USER_RUNNING_CONVECTION_SM/.local/`
    - `$CONFIG_PATH/convection-secrets/` (See [Configure the Server](#configure-the-server))<br/><br/>
    - Directory should be:
      - Owner: root (should be `$USER` if Step 1 was performed)
      - Group: root
      - Permissions: `4700` (`drws------`)<br/><br/>
    - Additionally Create `$SECRETS_CONFIG/certs/` (Same Permissions as above)
 3. Create a directory where the secrets will be stored (Referenced below as `$SECRET_STORE`)
    - Owner: root (should be `$USER` if Step 1 was performed)
    - Group: root
    - Permissions: `4700` (`drws------`)
 4. (Optional, Recommended) Create a python virtual env, and install modules from `requirements.txt` into it
 5. (Optional, Recommended) Copy `convection.secrets/convection-secrets.service` to `lib/systemd/system/`
    1. Ensure Paths for `ExecStart` and `PIDFile` are correct. `PIDFile` should match `{pid_dir}/convection-secrets.pid`
    2. If you used a virtual env from step 4, your `ExecStart` should look like `$PATH_TO_VENV/bin/convection-sm-server -v -c $SECRETS_CONFIG service-start`
    3. Run `sudo systemctl enable convection-secrets.service`

If you do not use the service file, you can stop the service by `Ctrl+C`, `kill -HUP` or `kill -TERM`

### Configure the Server

See [CONFIG.md](CONFIG.md) for configuration options.

#### Notes

 - If Networking is enabled (`service.use_network = true`) you should be sure to configure [Network ACLs](#network-acls-nacl) (`service.network.acl`)

### Initialization

Before Convection Secrets Manager can be used, it must be initialized. This involves creating the Root Key, Unlock Keys, and First User.

To Initialize:

 1. Start Convection Secrets Manager (systemd or by hand, if you didnt install the service config)
 2. Create a Public/Private Key Pair (same as the one from Step 3 of Setup, if you already did that).
 3. Run the following command: `convection-secrets-manager initialize --num-keys %KeyCount% --public-key /path/to/step1/public.key`

Initialization will generate some data that will not be shown again. Be sure to save it somewhere secure.

 - Unlock Keys
 - Access Key ID for `root` User.

### Configure the Client

If you do not wish to specify paths for the configuration file and AuthFile, you should use one of the paths mentioned below. Otherwise, you will need to use `--config` and `--auth-file` options on the commandline.

AuthFiles are not created by default. You need to create one in order for the AuthToken to be written to it

##### Configuration File

 - `~/.local/convection-secrets.client.[yaml,toml,json]`
 - `/etc/convection-secrets.client.[yaml,toml,json]`
 - `./convection-secrets.client.[yaml,toml,json]`

##### AuthFile File

 - `~/.local/convection-secrets.auth.[yaml,toml,json]`
 - `/etc/convection-secrets.auth.[yaml,toml,json]`
 - `./convection-secrets.auth.[yaml,toml,json]`


#### Client Configuration

The Client relies a configuration file to specify how to connect to the Server. A Minimal Configuration in TOML is below:

```toml
[global.secrets.client]
use_network = false
tls_ca = "/etc/convection-secrets/certs/ca.pem"
socket_path = "/var/run/convection.secrets.sock"
```

#### AuthFile Configuration

An AuthFile is an optional file you can use after initialization to provide authorization information without having to put it on the commandline. Not all entries are required.

```toml
private_key = "~/.local/convection-secrets.auth.key"
access_key_id = "<your user access key ID>"
key_password = "MyPrivateK3yP4ssw0rd" # Optional, only needed if Public/Private Pair is password protected.
```

An `authorize` call must still be called on the commandline. When an AuthFile is in use, instead of showing the AuthToken to stdout, the token is writen to the AuthFile. Once this is done, further commands can be executed without having to specify either option.

## Operational Notes

### Key Rotation

#### Root Key / Unlock Key Rotation `rotate_root_keys`

During this operation, new Unlock Keys are generated, a new Root Key is generated and encrypted, and then all KeySets and the KeyMapDB are re-encrypted. This will provide a new list of Unlock Keys to the user.

Once everything has been rotated, the system is Locked, and one of the new Unlock Keys must be passed to the system for further operation.

If this operation Fails, all files are reverted using their backup, the original Root Key and Unlock Keys will still be usable.

#### KeySet Rotation `rotate_keyset`

KeySet rotation involves generating new Keys for the KeySet, followed by re-encrypting every Secret Store associated with the KeySet. 

Because this operation relies on the underlying Secrets Store Plugin, it is possible that a rotation operation may fail. If the operation encounters an error during the rotation of a Secrets Store, then all other rotations are canceled, successful rotations are then attempted to be reverted to use the original KeySet Keys.

***DANGER*** **DANGER** ***DANGER*** **DANGER** ***DANGER*** **DANGER** ***DANGER*** **DANGER** 

**If a reversion fails, Secrets Stores associated with this KeySet may be in danger of being unusable. The Server will be shutdown to prevent further modifications until it can be examined by an admin. The new KeySet Keys will be stored as the KeySet Name `ROTATED_{keyset_name}`, while the original KeySet Keys will remain in `{keyset_name}`. Any Secrets Stores associated with this KeySet should be encrypted using one of these KeySets. You can manually rename the KeySet between the `ROTATED` and original version in order to save your secrets. If any problem arises from such reversion or rotation failure, the problem should be brought to the Secrets Store Plugin Developer.**

### User / Group Management

The `root` and `recovery` User Names are 'protected'. They cannot be deleted entirely; at least one Access Key ID must exist once the user exists. (Note that the `recovery` User does not exist at Initialization, and must be created, if you wish).

## Internals

### Unlock Keys

An Unlock Key is a key used to gain access to the [KeyDB](#the-keydb). When a server is initialized, a number of these keys are created, based on the input arg `--num-keys` (default 5) these keys are provided to the user once, and will never be displayed again. These Keys should be kept in a safe place, and should never be seen by untrusted eyes. Choose one of the provided unlock keys for continued use, then store these keys securely elsewhere.

****WARNING: Unlock Keys are the 'keys to the kingdom'. Loss of all unlock keys will result in permanent data loss. An attacker gaining access to Unlock Keys can enable them full access to all of your stored secrets****

****WARNING: BECAUSE AN UNLOCK KEY MUST BE PROVIDED AFTER STARTUP, THIS UNLOCK KEY MAY BE SEEN IN BASH HISTORY, ETC. BE SURE THAT YOU CLEAR HISTORY, OR USE A MEANS OF NOT LOGGING THE UNLOCK KEY, SUCH AS A SCRIPT OR AS AN ENV VARIABLE, ETC****

[Key Rotation](#rotation) should occur occasionally for security.

#### Rotation

Unlock Keys should be periodically rotated to ensure that if they are compromised, they do not remain in use for long. Rotation of Unlock Keys will create new Unlock Keys and KeyDBs from the currently unlocked KeyDB. The new Unlock Keys will be provided to the user once.

#### Revocation

Unlock Key Revocation can be performed by rotating Unlock Keys. Because determining which Root Key entry is the affected one would require a decryption attempt using that key, it is recommended to just perform [Key Rotation](#rotation) instead.

### Locking / Unlocking

Locking and Unlocking is a part of the process to gaining access to the Secrets Manager. When the server starts up, all secrets and [KeySets](#keysets) are encrypted. An [Unlock Key](#unlock-keys) must be sent using the `unlock` command. The Server will attempt to unlock the [KeyDB](#the-keydb) using the provided key. If successful, operation can continue.

### The KeyDB

The KeyDB is comprised of many pieces. Each piece is described in detail below. At Initialization a Root Key, KeyMapDB, and AuthDB are created. These 3 pieces comprise the core of Encryption/Decryption and Authorization.

*****WARNING: The components of the KeyDB should be treated as sensitive, and should be securely stored, and backed up. Loss of these items in part, or in whole, will result in data loss*****

#### Root Key

Root Keys decrypt the KeyMapDB, AuthDB and KeySets. This key is encrypted multiple times based on the configuration flag `--num-keys` at initialization. Each encryption is generated using a different key (thus, the Unlock Keys). The encrypted results are stored in `$storage_path/root.key`. During Unlock, an Unlock Key is passed to the Server, and the Server attempts to decrypt each key located in the Root Keys file. On success, the Root Key is loaded, for future use.

*****WARNING: The Root Key is the 'Key to the Kingdom', gaining access to the decrypted Root Key can allow perpetrators to decrypt and manipulate data.*****

*****WARNING: The Root Key is a critical component. Loss of the Root Key will result in complete data loss*****

#### KeyMapDB

The KeyMapDB is the mapping of which KeySets are attached to which Secrets Storage. This file is kept encrypted, and is encrypted by the Root Key. The KeyMapDB is located at `$storage_path/keymap.db`

While this file is critical, loss of this file will not necessarily result in data loss. You would need to rebuild the KeyMapDB by creating new KeySets and Stores with the previous names, replacing the file contents with the original KeySet and Store.

#### AuthDB

The AuthDB is the Secret Store for Users, Groups and ACLs. This contains the mapping of Users and their Access Key Pairs, as well as active Auth Tokens. The AuthDB is stored at `$storage_path/auth.db`. A Separate KeySet is generated for the AuthDB, called `authdb`

#### KeySets

The KeyDB also contains the keys for each [Secret Store](#secret-storage). These Keys are used to encrypt/decrypt the content of the [Secret Store](#secret-storage). Similarly, to the [Root Keys](#root-keys), a number of Keys are used for each [Secret Store](#secret-storage), meaning that each time a write operation is performed on an item within the Secret Store, there is no guarantee that the same key will be used that was used the first time. These Keys are stored by name, which can be used for multiple Secret Stores. These keys are encrypted by the Root Key and stored at `$storage_path/$keyset_name.key`

### Access Key Pairs

Each [User](#users) can generate Access Key Pairs for themselves (and others if authorized). an Access Key Pair contains 3 parts:

 - Access Key ID: This is the ID used to determine which Public Key to to use
 - Access Private Key: This is the Key the user keeps
 - Access Public Key: This is the Key the Server gets when a user is created

The Public and Private Key are generated by the User. During user creation, the Public Key is sent to the Server. The Server then generates an Access Key Id for the User and Public Key. The user will need the Private Key and Access Key Id for authorization. These should be kept secure as they allow access to whatever Secrets the User has access to. The Public Key is sent to, and stored on the server. The Private Key is **never** sent to the server.

### Secret Storage

Not all Secrets are created equally. Secrets Storage provides a means to store many types of data using the same general API. Secrets Storage is made up of [Plugins](#plugins), each plugin defines how data is stored, allowing for an extensible way of securely storing anything.

The root of a Secret Store contains a Metadata block, allowing for Plugin versioning, and additionally contains information like Storage Type, Creation Date, Creator, and Storage Name.

#### Plugins

A Secret Store is a way of securely storing a piece of data. Each Plugin defines how that data is stored. Some may define a single file that holds multiple secrets, another may define a directory with many individually encrypted files.

##### Plugin Types

  - Generic (`Generic_Secret`): Used for General Key/Value storage, can be used to store any text or binary data.
  - RSA (`RSA_Secret`): Used for RSA Keypair generation and storage. Can ingest existing RSA Keys and generate new ones.
  - Cert (`X509_Secret`): Used for x509 Certificate generation and storage. Can ingest existing certificates and generate new ones.
  - User (`User_Secret`): A more targeted Key/Value storage, for storing Usernames and Passwords

### Communication

Communication is done via Secure [Local Socket](#local-socket) using TLS 1.3+ and optionally a Secure [Network Socket](#networking) (also TLS 1.3+), as well as an optional [Web Socket](#websocket) (also TLS1.3+).

Each Inbound Request to the Server is in the format of: `<command> <request_data>`, where `request_data` is either empty or a JSON blob. Server Responses from the Server will be in a JSON blob. Data required for Request Data will depend on the incoming command. Response Data will always have the same format, and a minimal response.

#### Request Objects

See [API.md](API.md)

#### Response Object

```json
{
  __any_item__: ...., // Command Response Data
  "result": { // Result State
    "state": <bool>, // Success / Failure Flag
    "messages": <list[str]> // Messages from the command, etc.
  }
}
```

#### Local Socket

The Local Socket is an `AF_UNIX` socket with TLS 1.3+. The socket is setup as 0660. User/Group of the socket are controlled by `service.socket_owner` and `service.socket_group`.

#### Networking

Secrets can be accessed remotely by enabling `service.use_network` and then configuring the `service.network` block. By Default the network socket will listen on `127.0.0.1:9670`

##### Network ACLs (NACL)

For Network Enabled configurations, Convection Secrets Manager comes with a network-level ACL system, to be self contained. This is used to allow or deny the commands an IP address may execute. This is merely one level of access control. See [Users](#users) for the other part of access control.

NACLs are configured in the [Server Configuration](CONFIG.md) under `service.network.acl`

NACLs consist of 3 parts:

 - Type: Whether the ACL is for Allow or Deny operations
 - IP Address: IP Address or Subnet (in cidr)
 - Commands: List of Commands applicable to the NACL

##### Minimal NACLs

A set of NACLs are hardcoded into the Server to ensure functionality.

```json
{ 
  "type": "allow", 
  "ip_address": ["127.0.0.1"],
  "commands": [ "initialize", "unlock", "rotate", "authorize", "deauth" ]
},
{ 
  "type": "deny",
  "ip_address": ["0.0.0.0/0"],
  "commands": [ "service-stop", "stop", "service-start", "start" ]
}
```

#### WebSocket

A WebSocket can be enabled for the WebUI by enabling `service.use_websocket` and then configuring the `service.websocket` block. By Default the websocket will listen on `127.0.0.1:9671`

NACLs from the `service.network` block are used for the WebSocket. The WebSocket does not support using its own NACLs.

### Groups

Groups are simple containers that group together ACLs and Users. ACLs and Users are attached to a Group, which allows for easier management / application of ACLs.

### Users

Many of the CLI and API commands require authorization in order for the command to be accessible. This authorization is done with the use of an [Access Key Pair](#access-key-pairs), which provides an [Access Token](#access-tokens), which is used for subsequent commands. A User can generate multiple pairs, but these should be limited, to prevent one being lost to the ether and later compromised. Users are granted access per [Secret Store](#secret-storage), and optionally per secret. [User Access](#user--group-acls) is managed via ACLs

#### Access Tokens

After a User performs an `authorize` command, an Access Token is returned. This token is time limited (configurable). Once a user has the token, they can then perform other commands, while passing the recieved token along with their Access Key ID. Access Token expirations are controlled on two levels, at the service configuration level via `secrets.manager.authentication.token_max_expire`, and at token creation time. Expiration values at the Token level cannot exceed the `token_max_expire` value.

### User / Group ACLs

User and Group Level ACLs exist to restrict operations within Convection Secrets Manager. Each ACL type provides a different method for control. Commands perform an ACL check before performing their operation.

#### ACL Type - Generic (`ACLObject`)

This is the basis for other ACL Types, and its arguments are required for other ACL Types.

Arguments:
 - `name`: ACL Name, must be unique
 - `mode`: Allow / Deny mode.
   - In Console mode use `"allow"` and `"deny"`
   - In API / Server use `ACLObject.MODE_(ALLOW|DENY)`
 - `access_mode`: Specifies what types of access are allowed/disallowed, such as Read/Write/Modify/Delete
   - In Console mode use shorthand flags combined as needed: `r` (Read), `w` (Write), `m` (Modify), `d` (Delete)
   - In API / Server use `ACLObject.ACCESS_(READ|WRITE|MODIFY|DELETE|NONE)`, these can be AND'd or OR'd together to form various combinations

#### ACL Type - Command (`ACLCommand`)

This is a Command only limiter, allowing or preventing access to specific commands (such as `create_acl`, etc)

Arguments:
 - `commands`: A list of regex patterns (as strings) to match against

#### ACL Type - Store (`ACLStore`)

This is a Secrets / Store only limiter, allowing or preventing access to specific Secrets Stores or Secrets.

Arguments:
 - `store_paths`: A list of regex patterns (as strings) to check Secrets Storage path against
 - `secret_names`: A list of regex patterns (as strings) to check Secret Names against

## Extra Notes

Shutting Down the server does not involve calling the `convection-secrets-manager` command, instead it is terminated via `kill`. The table below indicates which signals will shutdown or restart

| Signal | Purpose | Linux | Windows |
|--------|---------|-------|---------|
| **CTRL_C_EVENT** | Shutdown | [ ] | [x] |
| **SIGINT** | Shutdown | [x]  | [x] |
| **SIGABRT** | Shutdown | [x] | [ ] |
| **SIGILL** | Shutdown | [x] | [ ] |
| **SIGTERM** | Shutdown | [x] | [ ] |
| **SIGHUP** | Restart | [x] | [ ] |

In the event that the service gets stuck trying to start or stop, you can kill the service with a `kill -9 <pid>`. All Signals above will cause a graceful shutdown attempt.
