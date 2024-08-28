from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.list_detection_rules_response_data import ListDetectionRulesResponseData
from typing import cast
from ...models.list_detection_rules_request_data import ListDetectionRulesRequestData
from typing import Dict



def _get_kwargs(
    *,
    body: ListDetectionRulesRequestData,

) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}


    

    

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/v1/detection_rule",
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[ListDetectionRulesResponseData]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ListDetectionRulesResponseData.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[ListDetectionRulesResponseData]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: ListDetectionRulesRequestData,

) -> Response[ListDetectionRulesResponseData]:
    """ List all detection rules under the provided tenant id.

     List all detection rules under the provided tenant id.

    Args:
        body (ListDetectionRulesRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListDetectionRulesResponseData]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    body: ListDetectionRulesRequestData,

) -> Optional[ListDetectionRulesResponseData]:
    """ List all detection rules under the provided tenant id.

     List all detection rules under the provided tenant id.

    Args:
        body (ListDetectionRulesRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListDetectionRulesResponseData
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: ListDetectionRulesRequestData,

) -> Response[ListDetectionRulesResponseData]:
    """ List all detection rules under the provided tenant id.

     List all detection rules under the provided tenant id.

    Args:
        body (ListDetectionRulesRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListDetectionRulesResponseData]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    body: ListDetectionRulesRequestData,

) -> Optional[ListDetectionRulesResponseData]:
    """ List all detection rules under the provided tenant id.

     List all detection rules under the provided tenant id.

    Args:
        body (ListDetectionRulesRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListDetectionRulesResponseData
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
