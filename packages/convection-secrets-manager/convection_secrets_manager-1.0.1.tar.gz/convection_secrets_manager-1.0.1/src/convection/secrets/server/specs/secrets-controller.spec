{
    "pid_dir": {
        "type": "dir:exist",
        "required": true,
        "default": "/var/run/convection-secrets/",
        "comment": "Directory to store Process ID"
    },
    "service": {
        "type": "dict",
        "required": true,
        "default": {},
        "comment": "Service Configuration",
        "spec_chain": "service"
    },
    "config": {
        "type": "dict",
        "required": true,
        "default": {},
        "comment": "Convection Secrets Configuration",
        "spec_chain": "service.config"
    }
}