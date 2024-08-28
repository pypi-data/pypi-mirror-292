from typing import Optional

from .http_err import get_body_and_handle_err
from .raw_api.api.event_sink import \
    list_event_sinks, create_event_sink, get_event_sink, update_event_sink, delete_event_sink
from .raw_api.models import ListEventSinksRequestData, CreateEventSinkRequestData, \
    EventSink as EventSinkJson, UpdateEventSinkRequestData, CreateEventSinkArgsType0, \
    CreateEventSinkArgsType1, CreateSlackEventSinkArgs, CreateWebhookEventSinkArgs, \
    UpdateEventSinkArgsType0, UpdateEventSinkArgsType1, UpdateSlackEventSinkArgs, \
    UpdateWebhookEventSinkArgs, DeleteEventSinkResponseData
from .raw_api.client import AuthenticatedClient
from .raw_api.types import Unset, UNSET

CreateEventSinkArgs = CreateEventSinkArgsType0 | CreateEventSinkArgsType1
UpdateEventSinkArgs = UpdateEventSinkArgsType0 | UpdateEventSinkArgsType1


def create_slack_event_sink_args(
    channel: str,
    slack_oauth_code: str
) -> CreateEventSinkArgsType0:
    return CreateEventSinkArgsType0(
        slack=CreateSlackEventSinkArgs(
            channel=channel,
            slack_oauth_code=slack_oauth_code
        )
    )


def create_webhook_event_sink_args(url: str) -> CreateEventSinkArgsType1:
    return CreateEventSinkArgsType1(
        webhook=CreateWebhookEventSinkArgs(
            url=url
        )
    )


def update_slack_event_sink_args(channel: str) -> UpdateEventSinkArgsType0:
    return UpdateEventSinkArgsType0(
        slack=UpdateSlackEventSinkArgs(
            channel=channel,
        )
    )


def update_webhook_event_sink_args(url: str) -> UpdateEventSinkArgsType1:
    return UpdateEventSinkArgsType1(
        webhook=UpdateWebhookEventSinkArgs(
            url=url
        )
    )


class EventSink():
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client


    def list_all(self, tenant_id: str) -> list[EventSinkJson]:
        req_body = ListEventSinksRequestData(
            tenant_id=tenant_id
        )

        resp = list_event_sinks.sync_detailed(
            client=self._client,
            body=req_body
        )
        
        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sinks


    def create(
        self,
        tenant_id: str,
        name: str,
        description: str,
        event_sink_args: CreateEventSinkArgs
    ) -> EventSinkJson:
        req_body = CreateEventSinkRequestData(
            tenant_id=tenant_id,
            name=name,
            description=description,
            event_sink_args=event_sink_args
        )

        resp = create_event_sink.sync_detailed(
            client=self._client,
            body=req_body
        )
        
        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sink


    def get(self, event_sink_id: str) -> EventSinkJson:
        resp = get_event_sink.sync_detailed(
            event_sink_id,
            client=self._client
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sink


    def update(
        self,
        event_sink_id: str,
        name: str | Unset = UNSET,
        description: str | Unset = UNSET,
        event_sink_args: UpdateEventSinkArgs | Unset = UNSET
    ) -> EventSinkJson:
        req_body = UpdateEventSinkRequestData(
            id=event_sink_id,
            name=name,
            description=description,
            event_sink_args=event_sink_args
        ) 

        resp = update_event_sink.sync_detailed(
            event_sink_id,
            client=self._client,
            body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sink


    def delete(self, event_sink_id: str) -> DeleteEventSinkResponseData:
        resp = delete_event_sink.sync_detailed(
            event_sink_id,
            client=self._client
        )
        
        return get_body_and_handle_err(resp)


class AsyncEventSink():
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client


    async def list_all(self, tenant_id: str) -> list[EventSinkJson]:
        req_body = ListEventSinksRequestData(
            tenant_id=tenant_id
        )

        resp = await list_event_sinks.asyncio_detailed(
            client=self._client,
            body=req_body
        )
        
        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sinks


    async def create(
        self,
        tenant_id: str,
        name: str,
        description: str,
        event_sink_args: CreateEventSinkArgs
    ) -> EventSinkJson:
        req_body = CreateEventSinkRequestData(
            tenant_id=tenant_id,
            name=name,
            description=description,
            event_sink_args=event_sink_args
        )

        resp = await create_event_sink.asyncio_detailed(
            client=self._client,
            body=req_body
        )
        
        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sink


    async def get(self, event_sink_id: str) -> EventSinkJson:
        resp = await get_event_sink.asyncio_detailed(
            event_sink_id,
            client=self._client
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sink


    async def update(
        self,
        event_sink_id: str,
        name: str | Unset = UNSET,
        description: str | Unset = UNSET,
        event_sink_args: UpdateEventSinkArgs | Unset = UNSET
    ) -> EventSinkJson:
        req_body = UpdateEventSinkRequestData(
            id=event_sink_id,
            name=name,
            description=description,
            event_sink_args=event_sink_args
        ) 

        resp = await update_event_sink.asyncio_detailed(
            event_sink_id,
            client=self._client,
            body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sink


    async def delete(self, event_sink_id: str) -> DeleteEventSinkResponseData:
        resp = await delete_event_sink.asyncio_detailed(
            event_sink_id,
            client=self._client
        )
        
        return get_body_and_handle_err(resp)
