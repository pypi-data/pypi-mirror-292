# Configuration Options

- [Configuration Options](#configuration-options)
  - [Spec for secrets-controller](#spec-for-secrets-controller)
  - [Spec for service](#spec-for-service)
  - [Spec for service.config](#spec-for-serviceconfig)
  - [Spec for service.network](#spec-for-servicenetwork)
  - [Spec for nacl.item](#spec-for-naclitem)
  - [Spec for nacl.root](#spec-for-naclroot)
  - [Spec for secrets.manager](#spec-for-secretsmanager)
  - [Spec for secrets.manager.authentication](#spec-for-secretsmanagerauthentication)
  - [Spec for plugin.secret](#spec-for-pluginsecret)

Auto generated from .spec files
## Spec for secrets-controller

Option: `pid_dir` - Directory to store Process ID
 - Type: dir
 - Required: True
 - Default: /var/run/convection-secrets/

Option: `service` - Service Configuration
 - Type: dict
 - Required: True
 - Default: {}
 - Additionally Validates With: `service`

Option: `config` - Convection Secrets Configuration
 - Type: dict
 - Required: True
 - Default: {}
 - Additionally Validates With: `service.config`

## Spec for service

Option: `socket_path` - Socket filename for IPC communication
 - Type: file
 - Required: True
 - Default: /var/run/convection.secrets.sock

Option: `socket_owner` - Unix Owner of Socket
 - Type: str
 - Required: True
 - Default: root

Option: `socket_group` - Unix Group for Socket
 - Type: str
 - Required: True
 - Default: root

Option: `use_network` - Create TCP Listener instead of IPC only
 - Type: bool
 - Required: True
 - Default: False

Option: `network` - Service Network configuration
 - Type: dict
 - Required: True
 - Default: {}
 - Additionally Validates With: `service.network`

Option: `tls_cert` - TLS Certificate Chain (Full Chain, except Key)
 - Type: file:exist
 - Required: True
 - Default: ./cert.pem

Option: `tls_key` - TLS Key for Cert
 - Type: file:exist
 - Required: True
 - Default: ./key.pem

Option: `tls_ca` - TLS CA for Cert
 - Type: str
 - Required: True
 - Default: 

Option: `tls_password` - Password for TLS Key
 - Type: str
 - Required: True
 - Default: 

Option: `log_file` - Log File Path
 - Type: file
 - Required: True
 - Default: ./convection-secrets.server.log

## Spec for service.config

Option: `path` - Secrets Storage Path
 - Type: dir
 - Required: True
 - Default: ./config/secrets/

Option: `manager` - Secrets Management configuration
 - Type: dict
 - Required: True
 - Default: {}
 - Additionally Validates With: `secrets.manager`

## Spec for service.network

Option: `listen_ip` - IP to Listen on
 - Type: str
 - Required: True
 - Default: 127.0.0.1

Option: `listen_port` - Port number to Listen on
 - Type: int
 - Required: True
 - Default: 9670

Option: `acl` - Access Control Configuration, for Network use
 - Type: list
 - Required: False
 - Default: []
 - Additionally Validates With: `nacl.item`

## Spec for nacl.item

Option: `__any_item__` - Network ACL Entry
 - Type: dict
 - Required: False
 - Default: {}
 - Additionally Validates With: `nacl.root`

## Spec for nacl.root

Option: `type` - ACL Type
 - Type: str
 - Required: True
 - Default: deny
 - Acceptable Values: allow, deny

Option: `ip_address` - IP Addresses to allow/deny
 - Type: list
 - Required: True
 - Default: []

Option: `commands` - List of commands to allow/deny
 - Type: list
 - Required: False
 - Default: []

## Spec for secrets.manager

Option: `keydb_key_count` - Number of Keys for each KeyDB to Create; SEE README REGARDING CHANGING THIS NUMBER
 - Type: int
 - Required: False
 - Default: 5

Option: `authentication` - Authentication Configuration
 - Type: dict
 - Required: True
 - Default: {}
 - Additionally Validates With: `secrets.manager.authentication`

Option: `__any_item__` - Placeholder
 - Type: any
 - Required: False

## Spec for secrets.manager.authentication

Option: `token_max_expire` - Auth Token maximum expiration time
 - Type: str
 - Required: True
 - Default: 10m
 - Acceptable Format: ^(\d+Y)?(\d+M)?(\d+w)?(\d+d)?(\d+h)?(\d+m)?(\d+s)?(\d+ms)?$
 - Example: ['4w10h', '1M', '10Y']

## Spec for plugin.secret

Option: `metadata` - Plugin Metadata
 - Type: dict
 - Required: True
 - Default: {}
 - Additionally Validates With: `metadata`

Option: `data` - Secrets Data Definitions
 - Type: dict
 - Required: False
 - Default: {}
 - Additionally Validates With: `anyitem`
