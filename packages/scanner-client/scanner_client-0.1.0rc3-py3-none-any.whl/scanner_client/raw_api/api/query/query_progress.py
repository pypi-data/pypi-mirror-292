from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.ad_hoc_query_progress_response import AdHocQueryProgressResponse
from typing import cast
from typing import Dict



def _get_kwargs(
    qr_id: str,

) -> Dict[str, Any]:
    

    

    

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/v1/query_progress/{qr_id}".format(qr_id=qr_id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[AdHocQueryProgressResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AdHocQueryProgressResponse.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[AdHocQueryProgressResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    qr_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[AdHocQueryProgressResponse]:
    """ Retrieve the state and current result set of a previously-started query.

     Retrieve the state and current result set of a previously-started query.

    Args:
        qr_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AdHocQueryProgressResponse]
     """


    kwargs = _get_kwargs(
        qr_id=qr_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    qr_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[AdHocQueryProgressResponse]:
    """ Retrieve the state and current result set of a previously-started query.

     Retrieve the state and current result set of a previously-started query.

    Args:
        qr_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AdHocQueryProgressResponse
     """


    return sync_detailed(
        qr_id=qr_id,
client=client,

    ).parsed

async def asyncio_detailed(
    qr_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[AdHocQueryProgressResponse]:
    """ Retrieve the state and current result set of a previously-started query.

     Retrieve the state and current result set of a previously-started query.

    Args:
        qr_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AdHocQueryProgressResponse]
     """


    kwargs = _get_kwargs(
        qr_id=qr_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    qr_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[AdHocQueryProgressResponse]:
    """ Retrieve the state and current result set of a previously-started query.

     Retrieve the state and current result set of a previously-started query.

    Args:
        qr_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AdHocQueryProgressResponse
     """


    return (await asyncio_detailed(
        qr_id=qr_id,
client=client,

    )).parsed
