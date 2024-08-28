from typing import Optional

from .http_err import get_body_and_handle_err
from .raw_api.api.workspace import \
    list_workspaces, create_workspace, get_workspace, update_workspace, delete_workspace
from .raw_api.models import ListWorkspacesRequestData, CreateWorkspaceRequestData, \
    Workspace as WorkspaceJson, UpdateWorkspaceRequestData, DeleteWorkspaceResponseData
from .raw_api.client import AuthenticatedClient
from .raw_api.types import Unset, UNSET


class Workspace():
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client


    def list_all(self, tenant_id: str) -> list[WorkspaceJson]:
        req_body = ListWorkspacesRequestData(
            tenant_id=tenant_id
        )

        resp = list_workspaces.sync_detailed(
            client=self._client,
            body=req_body
        )
        
        resp_body = get_body_and_handle_err(resp)

        return resp_body.workspaces


    def create(
        self,
        tenant_id: str,
        name: str,
        description: str,
    ) -> WorkspaceJson:
        req_body = CreateWorkspaceRequestData(
            tenant_id=tenant_id,
            name=name,
            description=description,
        )

        resp = create_workspace.sync_detailed(
            client=self._client,
            body=req_body
        )
        
        resp_body = get_body_and_handle_err(resp)

        return resp_body.workspace


    def get(self, workspace_id: str) -> WorkspaceJson:
        resp = get_workspace.sync_detailed(
            workspace_id,
            client=self._client
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.workspace


    def update(
        self,
        workspace_id: str,
        name: str | Unset = UNSET,
        description: str | Unset = UNSET,
    ) -> WorkspaceJson:
        req_body = UpdateWorkspaceRequestData(
            id=workspace_id,
            name=name,
            description=description,
        ) 

        resp = update_workspace.sync_detailed(
            workspace_id,
            client=self._client,
            body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.workspace


    def delete(self, workspace_id: str) -> DeleteWorkspaceResponseData:
        resp = delete_workspace.sync_detailed(
            workspace_id,
            client=self._client
        )
        
        return get_body_and_handle_err(resp)


class AsyncWorkspace():
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client


    async def list_all(self, tenant_id: str) -> list[WorkspaceJson]:
        req_body = ListWorkspacesRequestData(
            tenant_id=tenant_id
        )

        resp = await list_workspaces.asyncio_detailed(
            client=self._client,
            body=req_body
        )
        
        resp_body = get_body_and_handle_err(resp)

        return resp_body.workspaces


    async def create(
        self,
        tenant_id: str,
        name: str,
        description: str,
    ) -> WorkspaceJson:
        req_body = CreateWorkspaceRequestData(
            tenant_id=tenant_id,
            name=name,
            description=description,
        )

        resp = await create_workspace.asyncio_detailed(
            client=self._client,
            body=req_body
        )
        
        resp_body = get_body_and_handle_err(resp)

        return resp_body.workspace


    async def get(self, workspace_id: str) -> WorkspaceJson:
        resp = await get_workspace.asyncio_detailed(
            workspace_id,
            client=self._client
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.workspace


    async def update(
        self,
        workspace_id: str,
        name: str | Unset = UNSET,
        description: str | Unset = UNSET,
    ) -> WorkspaceJson:
        req_body = UpdateWorkspaceRequestData(
            id=workspace_id,
            name=name,
            description=description,
        ) 

        resp = await update_workspace.asyncio_detailed(
            workspace_id,
            client=self._client,
            body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.workspace


    async def delete(self, workspace_id: str) -> DeleteWorkspaceResponseData:
        resp = await delete_workspace.asyncio_detailed(
            workspace_id,
            client=self._client
        )
        
        return get_body_and_handle_err(resp)
