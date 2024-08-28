from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_detection_rule_response_data import GetDetectionRuleResponseData
from typing import cast
from ...models.update_detection_rule_request_data import UpdateDetectionRuleRequestData
from typing import Dict



def _get_kwargs(
    id: str,
    *,
    body: UpdateDetectionRuleRequestData,

) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}


    

    

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": "/v1/detection_rule/{id}".format(id=id,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[GetDetectionRuleResponseData]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetDetectionRuleResponseData.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[GetDetectionRuleResponseData]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateDetectionRuleRequestData,

) -> Response[GetDetectionRuleResponseData]:
    """ Update the detection rule with the given id.

     Update the detection rule with the given id.

    Args:
        id (str):
        body (UpdateDetectionRuleRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDetectionRuleResponseData]
     """


    kwargs = _get_kwargs(
        id=id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateDetectionRuleRequestData,

) -> Optional[GetDetectionRuleResponseData]:
    """ Update the detection rule with the given id.

     Update the detection rule with the given id.

    Args:
        id (str):
        body (UpdateDetectionRuleRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetDetectionRuleResponseData
     """


    return sync_detailed(
        id=id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateDetectionRuleRequestData,

) -> Response[GetDetectionRuleResponseData]:
    """ Update the detection rule with the given id.

     Update the detection rule with the given id.

    Args:
        id (str):
        body (UpdateDetectionRuleRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDetectionRuleResponseData]
     """


    kwargs = _get_kwargs(
        id=id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateDetectionRuleRequestData,

) -> Optional[GetDetectionRuleResponseData]:
    """ Update the detection rule with the given id.

     Update the detection rule with the given id.

    Args:
        id (str):
        body (UpdateDetectionRuleRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetDetectionRuleResponseData
     """


    return (await asyncio_detailed(
        id=id,
client=client,
body=body,

    )).parsed
