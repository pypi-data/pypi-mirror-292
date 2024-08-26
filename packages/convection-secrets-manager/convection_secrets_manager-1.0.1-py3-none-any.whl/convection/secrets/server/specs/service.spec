{
    "socket_path": {
        "type": "file",
        "required": true,
        "default": "/var/run/convection.secrets.sock",
        "comment": "Socket filename for IPC communication"
    },
    "socket_owner": {
        "type": "str",
        "required": true,
        "default": "root",
        "comment": "Unix Owner of Socket"
    },
    "socket_group": {
        "type": "str",
        "required": true,
        "default": "root",
        "comment": "Unix Group for Socket"
    },
    "use_network": {
        "type": "bool",
        "required": true,
        "default": false,
        "comment": "Create TCP Listener instead of IPC only"
    },
    "network": {
        "type": "dict",
        "required": true,
        "default": {},
        "comment": "Service Network configuration",
        "spec_chain": "service.network"
    },
    "use_websocket": {
        "type": "bool",
        "required": true,
        "default": false,
        "comment": "Create a WebSocket Listener for WebUI usage. Must be enabled for WebUI"
    },
    "websocket": {
        "type": "dict",
        "required": true,
        "default": {},
        "comment": "Service WebSocket configuration. Must be configured for WebUI",
        "spec_chain": "service.websocket"
    },
    "tls_cert": {
        "type": "file:exist",
        "required": true,
        "default": "./cert.pem",
        "comment": "TLS Certificate Chain (Full Chain, except Key)"
    },
    "tls_key": {
        "type": "file:exist",
        "required": true,
        "default": "./key.pem",
        "comment": "TLS Key for Cert"
    },
    "tls_ca": {
        "type": "str",
        "required": true,
        "default": "",
        "comment": "TLS CA for Cert"
    },
    "tls_password": {
        "type": "str",
        "required": true,
        "default": "",
        "comment": "Password for TLS Key"
    },
    "log_file": {
        "type": "str",
        "required": true,
        "default": "./convection-secrets.server.log",
        "comment": "Log File Path"
    }
}