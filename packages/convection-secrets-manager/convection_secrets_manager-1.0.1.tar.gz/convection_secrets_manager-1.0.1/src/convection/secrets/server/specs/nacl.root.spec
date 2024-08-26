{
    "type": {
        "type": "str",
        "required": true,
        "default": "deny",
        "comment": "ACL Type",
        "values": [ "allow", "deny" ]
    },
    "ip_address": {
        "type": "list",
        "required": true,
        "default": [],
        "comment": "IP Addresses to allow/deny"
    },
    "commands": {
        "type": "list",
        "required": false,
        "default": [],
        "comment": "List of commands to allow/deny"
    }
}