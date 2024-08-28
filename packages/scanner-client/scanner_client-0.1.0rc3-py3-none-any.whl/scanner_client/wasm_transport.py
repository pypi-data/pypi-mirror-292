from typing import Mapping

"""
A custom HTTPX transport implementation for use in wasm environments. This file
should only be imported in wasm/jupyter builds, as it depends on the the urllib
3 package (patched in pyodide to use browser fetch), which we don't generally
want to express as a dependency.
"""
import httpx
import urllib3
import json

from pyodide.http import pyfetch # type: ignore

"""
TODO: this is a hack to disable warnings about insecure requests:
https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings

Since we only expect to run this in a jupyterlite/pyodide/wasm environment, this
is actually fine (the request isn't _actually_ insecure, because it eventually
is being handled by either `XmlHttpRequest` or `fetch` in the browser itself).
In fact, it may not even be possible to do verification python-side (since the
browser doesn't expose things like certificate info to "userspace" code).

However, it would probably be ideal to find a less-comprehensive way to quash
this warning.
"""
urllib3.disable_warnings()

class URLLib3Transport(httpx.BaseTransport):
    def handle_request(
        self,
        request: httpx.Request,
    ) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        urllib3_response = urllib3.request(
            request.method,
            str(request.url),
            headers=request.headers,
            json=payload,
            timeout=60,
            preload_content=False)

        body = urllib3_response.read()

        return httpx.Response(
            urllib3_response.status,
            headers = urllib3_response.headers,
            content = body,
        )

        
async def send_fetch(
    method: str,
    url: str,
    headers: Mapping[str, str],
    payload: str | bytes,
) -> httpx.Response:
    resp = await pyfetch(
        url,
        method=method,
        headers=headers,
        body=payload
    )

    return httpx.Response(
        resp.status,
        headers=resp.headers,
        content=await resp.bytes(),
    )


class AsyncFetchTransport(httpx.AsyncBaseTransport):
    # this is not technically async rn
    async def handle_async_request(
        self,
        request: httpx.Request,
    ) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))

        resp = await pyfetch(
            str(request.url),
            method=request.method,
            headers={k:v for k,v in request.headers.items()},
            body=json.dumps(payload)
        )

        return httpx.Response(
            resp.status,
            headers=resp.headers,
            content=await resp.bytes(),
        )
