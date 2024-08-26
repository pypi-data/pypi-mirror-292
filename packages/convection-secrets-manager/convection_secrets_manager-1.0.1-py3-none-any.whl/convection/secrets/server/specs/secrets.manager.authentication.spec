{
    "token_max_expire": {
        "type": "str",
        "required": true,
        "default": "10m",
        "comment": "Auth Token maximum expiration time",
        "format": "^(\\d+Y)?(\\d+M)?(\\d+w)?(\\d+d)?(\\d+h)?(\\d+m)?(\\d+s)?(\\d+ms)?$",
        "example": [ "4w10h", "1M", "10Y" ]
    }
}