{
    "path": {
        "type": "dir:exist",
        "required": true,
        "comment": "Secrets Storage Path",
        "default": "./config/secrets/"
    },
    "manager": {
        "type": "dict",
        "required": true,
        "default": {},
        "comment": "Secrets Management configuration",
        "spec_chain": "secrets.manager"
    }
}
