{
    "keydb_key_count": {
        "type": "int",
        "default": 5,
        "comment": "Number of Keys for each KeyDB to Create; SEE README REGARDING CHANGING THIS NUMBER"
    },
    "authentication": {
        "type": "dict",
        "default": {},
        "required": true,
        "comment": "Authentication Configuration",
        "spec_chain": "secrets.manager.authentication"
    },
    "__any_item__": {
        "type": "any",
        "required": false,
        "comment": "Placeholder"
    }
}