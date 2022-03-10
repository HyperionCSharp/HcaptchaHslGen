from .utils import parse_proxy_string
from http.client import HTTPConnection, HTTPSConnection, HTTPResponse
from typing import Union
from urllib.parse import urlsplit
import ssl

class HTTPClient:
    _default_ssl_context = ssl.create_default_context()

    def __init__(
        self,
        timeout: float = 5,
        blocksize: int = 104857, 
        proxy: Union[str, None] = None,
        ssl_context: Union[ssl.SSLContext, None] = None
    ):
        self._timeout = timeout
        self._blocksize = blocksize
        self._proxy_auth, self._proxy_addr = parse_proxy_string(proxy)
        self._ssl_context = ssl_context or self._default_ssl_context
        self._conn_map = {}

    def __enter__(self) -> "HTTPClient":
        return self
    
    def __exit__(self, *_) -> None:
        self.clear()

    def clear(self) -> None:
        for conn in self._conn_map.values():
            conn.close()
        self._conn_map = {}

    def request(
        self,
        method: str,
        url: str,
        headers: dict = None,
        body: Union[bytes, None] = None,
        **kwargs
        ) -> HTTPResponse:
        if isinstance(body, str): body = body.encode()
        p_url = urlsplit(url)
        path = p_url.path + (f"?{p_url.query}" if p_url.query else "")
        conn = self._get_conn(p_url.hostname, p_url.port,
                              ssl=(p_url.scheme == "https"))
        conn.request(method, path, body, headers or {}, **kwargs)
        resp = conn.getresponse()
        return resp
    
    def _get_conn(
        self,
        hostname: str = None,
        port: int = None,
        ssl: bool = True
        ) -> HTTPSConnection:
        conn_key = (hostname.lower(), port, ssl)
        conn_addr = (hostname.lower(), port or (443 if ssl else 80))

        if conn_key in self._conn_map:
            return self._conn_map[conn_key]

        if ssl:
            conn = HTTPSConnection(
                *(self._proxy_addr or conn_addr),
                timeout=self._timeout,
                context=self._ssl_context,
                blocksize=self._blocksize
            )
        else:
            conn = HTTPConnection(
                *(self._proxy_addr or conn_addr),
                timeout=self._timeout,
                blocksize=self._blocksize
            )
        
        if self._proxy_addr:
            conn.set_tunnel(*conn_addr, headers={
                "Proxy-Authorization": self._proxy_auth
            })

        self._conn_map[conn_key] = conn
        return conn