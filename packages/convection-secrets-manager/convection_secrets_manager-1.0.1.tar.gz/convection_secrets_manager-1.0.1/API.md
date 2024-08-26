# API and Command Documentation

- [API and Command Documentation](#api-and-command-documentation)
  - [Internal](#internal)
    - [Command: `start`](#command-start)
    - [Command: `stop`](#command-stop)
  - [General](#general)
    - [Command: `command_list`](#command-command_list)
    - [Command: `status`](#command-status)
    - [Command: `default_config`](#command-default_config)
    - [Command: `initialize`](#command-initialize)
      - [Arguments](#arguments)
    - [Command: `unlock`](#command-unlock)
      - [Arguments](#arguments-1)
    - [Command: `lock`](#command-lock)
    - [Command: `list_store_types`](#command-list_store_types)
  - [Key Management](#key-management)
    - [Command: `rotate_root_keys`](#command-rotate_root_keys)
      - [Arguments](#arguments-2)
    - [Command: `list_keysets`](#command-list_keysets)
    - [Command: `create_keyset`](#command-create_keyset)
      - [Arguments](#arguments-3)
    - [Command: `remove_keyset`](#command-remove_keyset)
      - [Arguments](#arguments-4)
    - [Command: `rotate_keyset`](#command-rotate_keyset)
      - [Arguments](#arguments-5)
  - [User Management](#user-management)
    - [Command: `authorize`](#command-authorize)
      - [Arguments](#arguments-6)
    - [Command: `deauth`](#command-deauth)
    - [Command: `audit_user`](#command-audit_user)
      - [Arguments](#arguments-7)
    - [Command: `list_users`](#command-list_users)
    - [Command: `create_user`](#command-create_user)
      - [Arguments](#arguments-8)
    - [Command: `remove_access`](#command-remove_access)
      - [Arguments](#arguments-9)
  - [Group Management](#group-management)
    - [Command: `audit_group`](#command-audit_group)
      - [Arguments](#arguments-10)
    - [Command: `list_groups`](#command-list_groups)
    - [Command: `create_group`](#command-create_group)
      - [Arguments](#arguments-11)
    - [Command: `attach_group`](#command-attach_group)
      - [Arguments](#arguments-12)
    - [Command: `detach_group`](#command-detach_group)
      - [Arguments](#arguments-13)
    - [Command: `remove_group`](#command-remove_group)
      - [Arguments](#arguments-14)
  - [ACL Management](#acl-management)
    - [Command: `audit_acl`](#command-audit_acl)
      - [Arguments](#arguments-15)
    - [Command: `list_acls`](#command-list_acls)
    - [Command: `create_acl`](#command-create_acl)
      - [Arguments](#arguments-16)
    - [Command: `attach_acl`](#command-attach_acl)
      - [Arguments](#arguments-17)
    - [Command: `detach_acl`](#command-detach_acl)
      - [Arguments](#arguments-18)
    - [Command: `remove_acl`](#command-remove_acl)
      - [Arguments](#arguments-19)
  - [Store Management](#store-management)
    - [Command: `list_stores`](#command-list_stores)
    - [Command: `create_store`](#command-create_store)
      - [Arguments](#arguments-20)
    - [Command: `remove_store`](#command-remove_store)
      - [Arguments](#arguments-21)
    - [Command: `store_config`](#command-store_config)
      - [Arguments](#arguments-22)
    - [Command: `store_info`](#command-store_info)
      - [Arguments](#arguments-23)
  - [Secret Management](#secret-management)
    - [Command: `list_secrets`](#command-list_secrets)
      - [Arguments](#arguments-24)
    - [Command: `create_secret`](#command-create_secret)
      - [Arguments](#arguments-25)
    - [Command: `get_secret`](#command-get_secret)
      - [Arguments](#arguments-26)
    - [Command: `update_secret`](#command-update_secret)
      - [Arguments](#arguments-27)
    - [Command: `destroy_secret`](#command-destroy_secret)
      - [Arguments](#arguments-28)

## Internal
### Command: `start`
Start Convection Secrets Manager

Authorization Required? **N**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **N**        |

Utilizes Access Modes: **Read (r, integer: 2)**

### Command: `stop`
Stop Convection Secrets Manager

Authorization Required? **N**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **N**        |

Utilizes Access Modes: **Read (r, integer: 2)**

## General
### Command: `command_list`
List of Commands

Authorization Required? **N**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

### Command: `status`
Get KeyDB Lock/Unlock Status

Authorization Required? **N**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

### Command: `default_config`
Create Default Configuration

Authorization Required? **N**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **N**        |

Utilizes Access Modes: **Read, Write, Modify, Delete (rwmd, integer: 30)**

### Command: `initialize`
Initialize new KeyDB (DESTRUCTIVE OPERATION)

Authorization Required? **N**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **N**        |

Utilizes Access Modes: **Read, Write, Modify, Delete (rwmd, integer: 30)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                                      | Required   | Type   | Default   |
|------------|---------------|--------------------------------------------------|------------|--------|-----------|
| num_keys   | --num-keys    | Number of Root Keys to Generate                  | **N**      | int    | 5         |
| public_key | --public-key  | Public Key to use for Root User, Path or Content | **Y**      | str    | None      |

### Command: `unlock`
Unlock KeyDB Database for Access

Authorization Required? **N**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **N**        |

Utilizes Access Modes: **Read (r, integer: 2)**

#### Arguments
| API Name   | CLI Flag(s)   | Description        | Required   | Type   | Default   |
|------------|---------------|--------------------|------------|--------|-----------|
| unlock_key | --unlock-key  | Key to unlock with | **Y**      | str    | None      |

### Command: `lock`
Re-lock KeyDB

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **N**        |

Utilizes Access Modes: **Read, Write (rw, integer: 6)**

### Command: `list_store_types`
List Store Type Names

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

## Key Management
### Command: `rotate_root_keys`
Rotate KeyDB Unlock Keys

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **N**        |

Utilizes Access Modes: **Read, Write, Modify (rwm, integer: 14)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                     | Required   | Type   |   Default |
|------------|---------------|---------------------------------|------------|--------|-----------|
| num_keys   | --num-keys    | Number of Root Keys to Generate | **N**      | int    |         5 |

### Command: `list_keysets`
List KeySets

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

### Command: `create_keyset`
Create new KeySet

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Write (w, integer: 4)**

#### Arguments
| API Name    | CLI Flag(s)   | Description           | Required   | Type   | Default   |
|-------------|---------------|-----------------------|------------|--------|-----------|
| keyset_name | --keyset-name | KeySet Name to create | **Y**      | str    | None      |

### Command: `remove_keyset`
Remove a KeySet. Must not have any associated Stores

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Delete (d, integer: 16)**

#### Arguments
| API Name    | CLI Flag(s)   | Description           | Required   | Type   | Default   |
|-------------|---------------|-----------------------|------------|--------|-----------|
| keyset_name | --keyset-name | KeySet Name to delete | **Y**      | str    | None      |

### Command: `rotate_keyset`
Rotate Keys in an Existing KeySet

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Modify (m, integer: 8)**

#### Arguments
| API Name    | CLI Flag(s)   | Description           | Required   | Type   | Default   |
|-------------|---------------|-----------------------|------------|--------|-----------|
| keyset_name | --keyset-name | KeySet Name to rotate | **Y**      | str    | None      |

## User Management
### Command: `authorize`
Authenticate With Server

Authorization Required? **N**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

#### Arguments
| API Name      | CLI Flag(s)     | Description                                                                                     | Required   | Type   | Default   |
|---------------|-----------------|-------------------------------------------------------------------------------------------------|------------|--------|-----------|
| access_key_id | --access-key-id | Access Key ID                                                                                   | **N**      | str    | None      |
| auth_file     | -A, --auth-file | AuthFile (See Documentation for usage)                                                          | **N**      | str    | None      |
| private_key   | --private-key   | Private Key, Path or Content                                                                    | **N**      | str    | None      |
| key_password  | --key-password  | Password for Private Key (if used)                                                              | **N**      | str    | None      |
| expire_time   | --expire-time   | Expiration Time; format is (\d+Y)?(\d+M)?(\d+w)?(\d+d)?(\d+h)?(\d+m)?(\d+s)?(\d+ms) (EX: 4h20m) | **N**      | str    | None      |

### Command: `deauth`
Logout/Deauthenticate

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

### Command: `audit_user`
Display User stats and ACL / Group attachment info

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                   | Required   | Type   | Default   |
|------------|---------------|-------------------------------|------------|--------|-----------|
| user_name  | --user-name   | User Name to display info for | **Y**      | str    | None      |

### Command: `list_users`
Display all registered User Names

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

### Command: `create_user`
Create New User and/or new Access Key ID

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Write, Modify (wm, integer: 12)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                                                                                                        | Required   | Type   | Default   |
|------------|---------------|--------------------------------------------------------------------------------------------------------------------|------------|--------|-----------|
| user_name  | --user-name   | Username to create                                                                                                 | **Y**      | str    | None      |
| public_key | --public-key  | Public Key to use for new User, Path or Content. For Console, Prefix with an `@` for file. EX: `@/path/to/pub.key` | **Y**      | str    | None      |

### Command: `remove_access`
Remove a User / Access Key ID / Public Key, see docs for info

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Modify, Delete (md, integer: 24)**

#### Arguments
| API Name             | CLI Flag(s)            | Description                                                                          | Required   | Type   | Default   |
|----------------------|------------------------|--------------------------------------------------------------------------------------|------------|--------|-----------|
| user_name            | --user-name            | Username to Operate on, if known, or to remove completely, if no --remove-* provided | **N**      | str    | None      |
| remove_access_key_id | --remove-access-key-id | Access Key ID to Remove/Revoke                                                       | **N**      | str    | None      |
| remove_public_key    | --remove-public-key    | Public Key to Remove/Revoke                                                          | **N**      | str    | None      |

## Group Management
### Command: `audit_group`
Display Users and ACLs attached to Group

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                   | Required   | Type   | Default   |
|------------|---------------|-------------------------------|------------|--------|-----------|
| group_name | --group-name  | User Name to display info for | **Y**      | str    | None      |

### Command: `list_groups`
Display all registered Group Names

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

### Command: `create_group`
Create a new AuthDB Group

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Write (w, integer: 4)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                           | Required   | Type   | Default   |
|------------|---------------|---------------------------------------|------------|--------|-----------|
| group_name | --group-name  | Group Name to create (Must be unique) | **Y**      | str    | None      |

### Command: `attach_group`
Attach Group to User

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Write, Modify (wm, integer: 12)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                 | Required   | Type   | Default   |
|------------|---------------|-----------------------------|------------|--------|-----------|
| user_name  | --user-name   | User Name to Add to Group   | **Y**      | str    | None      |
| group_name | --group-name  | Group Name to place User in | **Y**      | str    | None      |

### Command: `detach_group`
Remove a User from a Group

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Modify, Delete (md, integer: 24)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                    | Required   | Type   | Default   |
|------------|---------------|--------------------------------|------------|--------|-----------|
| user_name  | --user-name   | User Name to Remove from Group | **Y**      | str    | None      |
| group_name | --group-name  | Group Name to remove User from | **Y**      | str    | None      |

### Command: `remove_group`
Destroy Group (Remove Users from Group, Delete Group)

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Modify, Delete (md, integer: 24)**

#### Arguments
| API Name   | CLI Flag(s)   | Description           | Required   | Type   | Default   |
|------------|---------------|-----------------------|------------|--------|-----------|
| group_name | --group-name  | Group Name to destroy | **Y**      | str    | None      |

## ACL Management
### Command: `audit_acl`
Display ACL information

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                  | Required   | Type   | Default   |
|------------|---------------|------------------------------|------------|--------|-----------|
| acl_name   | --acl-name    | ACL Name to display info for | **Y**      | str    | None      |

### Command: `list_acls`
Display all registered ACLs

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

### Command: `create_acl`
Create a new User / Group ACL

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Write (w, integer: 4)**

#### Arguments
| API Name     | CLI Flag(s)   | Description                                                                                                   | Required   | Type   | Default   |
|--------------|---------------|---------------------------------------------------------------------------------------------------------------|------------|--------|-----------|
| mode         | --mode        | Set ACL as Allow (allow) / Deny (deny)                                                                        | **Y**      | str    | None      |
| access_mode  | --access-mode | Set Access Type allow/disallow, combined as needed. `r` (Read), `w` (Write), `m` (Modify), `d` (Delete)       | **Y**      | str    | None      |
| acl_name     | --acl-name    | ACL Name, must be unique                                                                                      | **Y**      | str    | None      |
| acl_type     | --acl-type    | Type of ACL to create. See Documentation                                                                      | **Y**      | str    | None      |
| commands     | --command     | Regex Pattern(s) to check commands against; Required when ACL Type is ACLCommand                              | **N**      | str    | None      |
| store_paths  | --store-path  | Regex Pattern(s) to check Secrets Storage Paths against; (One of, or Both) Required when ACL Type is ACLStore | **N**      | str    | None      |
| secret_names | --secret-name | Regex Pattern(s) to check Secrets Names against; (One of, or Both) Required when ACL Type is ACLStore         | **N**      | str    | None      |

### Command: `attach_acl`
Attach ACL to User or Group

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Write, Modify (wm, integer: 12)**

#### Arguments
| API Name    | CLI Flag(s)   | Description                                 | Required   | Type   | Default   |
|-------------|---------------|---------------------------------------------|------------|--------|-----------|
| acl_name    | --acl-name    | ACL Name to attach                          | **Y**      | str    | None      |
| attach_type | --attach-type | Attach to type; Group (group) / User (user) | **Y**      | str    | None      |
| attach_name | --attach-name | Name of Group or User to attach ACL to      | **Y**      | str    | None      |

### Command: `detach_acl`
Remove ACL to User or Group

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Modify, Delete (md, integer: 24)**

#### Arguments
| API Name    | CLI Flag(s)   | Description                                   | Required   | Type   | Default   |
|-------------|---------------|-----------------------------------------------|------------|--------|-----------|
| acl_name    | --acl-name    | ACL Name to attach                            | **Y**      | str    | None      |
| detach_type | --detach-type | Detach from type; Group (group) / User (user) | **Y**      | str    | None      |
| detach_name | --detach-name | Name of Group or User to detach ACL from      | **Y**      | str    | None      |

### Command: `remove_acl`
Destroy ACL (Completely Remove from Groups, Delete entirely)

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Modify, Delete (md, integer: 24)**

#### Arguments
| API Name   | CLI Flag(s)   | Description         | Required   | Type   | Default   |
|------------|---------------|---------------------|------------|--------|-----------|
| acl_name   | --acl-name    | ACL Name to destroy | **Y**      | str    | None      |

## Store Management
### Command: `list_stores`
List Secrets Stores

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

### Command: `create_store`
Create a new Secrets Store

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Write (w, integer: 4)**

#### Arguments
| API Name    | CLI Flag(s)   | Description                                                                                                                                               | Required   | Type   | Default   |
|-------------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|------------|--------|-----------|
| store_name  | --store-name  | Secrets Store Name / Path to create. Must be unique                                                                                                       | **Y**      | str    | None      |
| keyset_name | --keyset-name | KeySet Name to use for Store                                                                                                                              | **Y**      | str    | None      |
| store_type  | --store-type  | Secrets Store Storage Type                                                                                                                                | **Y**      | str    | None      |
| store_args  | --store-arg   | Secrets Store specific args, in the form of `key=value`, or json string. See Documentation for Secrets Store type of the Secret Store you're operating on | **N**      | str    | None      |

### Command: `remove_store`
Remove a Secrets Store and all of its data

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Delete (d, integer: 16)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                         | Required   | Type   | Default   |
|------------|---------------|-------------------------------------|------------|--------|-----------|
| store_name | --store-name  | Secrets Store Name / Path to delete | **Y**      | str    | None      |

### Command: `store_config`
View / Set Secrets Store Configuration Data

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read, Write (rw, integer: 6)**

#### Arguments
| API Name    | CLI Flag(s)   | Description                                                                                                                                                 | Required   | Type   | Default   |
|-------------|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|------------|--------|-----------|
| store_name  | --store-name  | Secrets Store Name to view/set Configuration for                                                                                                            | **Y**      | str    | None      |
| config_args | --config-arg  | Secrets Store Configuration specific args, in the form of `key=value`. See Documentation for the Secrets Store type of the Secret Store you're operating on | **N**      | str    | None      |

### Command: `store_info`
View Secrets Store Stats and Information

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read, Write (rw, integer: 6)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                                | Required   | Type   | Default   |
|------------|---------------|--------------------------------------------|------------|--------|-----------|
| store_name | --store-name  | Secrets Store Name to view Information for | **Y**      | str    | None      |

## Secret Management
### Command: `list_secrets`
List Registered Secrets in Secret Store

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                                                                                                                               | Required   | Type   | Default   |
|------------|---------------|-------------------------------------------------------------------------------------------------------------------------------------------|------------|--------|-----------|
| store_name | --store-name  | Secrets Store Name to List Secrets from                                                                                                   | **Y**      | str    | None      |
| store_args | --store-arg   | Secrets Store specific args, in the form of `key=value`. See Documentation for Secrets Store type of the Secret Store you're operating on | **N**      | str    | None      |

### Command: `create_secret`
Create a new Secret within an existing Secret Store

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Write (w, integer: 4)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                                                                                                                                   | Required   | Type   | Default   |
|------------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------|------------|--------|-----------|
| store_name | --store-name  | Secrets Store Name to add Secret to                                                                                                           | **Y**      | str    | None      |
| store_args | --store-arg   | Secrets Store specific args, in the form of `key=value`. See Documentation for the Secrets Store type of the Secret Store you're operating on | **N**      | str    | None      |

### Command: `get_secret`
Get Secret Data from Secret Store

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Read (r, integer: 2)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                                                                                                                               | Required   | Type   | Default   |
|------------|---------------|-------------------------------------------------------------------------------------------------------------------------------------------|------------|--------|-----------|
| store_name | --store-name  | Secrets Store Name to Get Secret From                                                                                                     | **Y**      | str    | None      |
| store_args | --store-arg   | Secrets Store specific args, in the form of `key=value`. See Documentation for Secrets Store type of the Secret Store you're operating on | **N**      | str    | None      |

### Command: `update_secret`
Update an existing Secret in a Secret Store

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Modify (m, integer: 8)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                                                                                                                                   | Required   | Type   | Default   |
|------------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------|------------|--------|-----------|
| store_name | --store-name  | Secrets Store Name to add Secret to                                                                                                           | **Y**      | str    | None      |
| store_args | --store-arg   | Secrets Store specific args, in the form of `key=value`. See Documentation for the Secrets Store type of the Secret Store you're operating on | **N**      | str    | None      |

### Command: `destroy_secret`
Create a new Secret within an existing Secret Store

Authorization Required? **Y**

| Access Method   | Available?   |
|-----------------|--------------|
| CLI             | **Y**        |
| API             | **Y**        |

Utilizes Access Modes: **Delete (d, integer: 16)**

#### Arguments
| API Name   | CLI Flag(s)   | Description                                                                                                                                   | Required   | Type   | Default   |
|------------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------|------------|--------|-----------|
| store_name | --store-name  | Secrets Store Name to add Secret to                                                                                                           | **Y**      | str    | None      |
| store_args | --store-arg   | Secrets Store specific args, in the form of `key=value`. See Documentation for the Secrets Store type of the Secret Store you're operating on | **N**      | str    | None      |


