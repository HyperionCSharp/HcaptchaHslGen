from base64 import b64encode

def parse_proxy_string(proxy_str):
    if not proxy_str:
        return None, None

    proxy_str = proxy_str.rpartition("://")[2]
    auth, _, fields = proxy_str.rpartition("@")
    fields = fields.split(":", 2)

    if len(fields) == 2:
        hostname, port = fields
        if auth:
            auth = "Basic " + b64encode(auth.encode()).decode()
        addr = (hostname.lower(), int(port))
        return auth, addr

    elif len(fields) == 3:
        hostname, port, auth = fields
        auth = "Basic " + b64encode(auth.encode()).decode()
        addr = (hostname.lower(), int(port))
        return auth, addr
    
    raise Exception(f"Unrecognized proxy format: {proxy_str}")