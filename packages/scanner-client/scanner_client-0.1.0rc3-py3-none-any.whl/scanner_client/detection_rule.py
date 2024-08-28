from typing import Optional

from .http_err import get_body_and_handle_err
from .raw_api.api.detection_rule import \
    list_detection_rules, create_detection_rule, get_detection_rule, \
        update_detection_rule, delete_detection_rule
from .raw_api.models import ListDetectionRulesRequestData, CreateDetectionRuleRequestData, DeleteDetectionRuleResponseData,\
    DetectionRule as DetectionRuleJson, \
    DetectionRuleSummary, \
    UpdateDetectionRuleRequestData, \
    DetectionSeverityType0, DetectionSeverityType1, DetectionSeverityType2, DetectionSeverityType3, \
    DetectionSeverityType4, DetectionSeverityType5, DetectionSeverityType6, DetectionSeverityType7, \
    PermsByRoleForRbacDetectionRulePermissionType, PermsByRoleForRbacDetectionRulePermissionTypePermissionsByRole, \
    RbacDetectionRulePermissionType
from .raw_api.client import AuthenticatedClient
from .raw_api.types import Unset, UNSET

# TODO: this is currently kinda awkward to deal with. Ideally we can get the
# openapi schema to just include a single DetectionSeverity enum, instead of a
# union type across 7 enums each with one variant.
DetectionSeverity = DetectionSeverityType0 \
    | DetectionSeverityType1 \
    | DetectionSeverityType2 \
    | DetectionSeverityType3 \
    | DetectionSeverityType4 \
    | DetectionSeverityType5 \
    | DetectionSeverityType6 \
    | DetectionSeverityType7

def starting_permissions_for_detection_rule(
    starting_permissions: dict[str, list[RbacDetectionRulePermissionType]]
) -> PermsByRoleForRbacDetectionRulePermissionType:
    return PermsByRoleForRbacDetectionRulePermissionType(
        permissions_by_role=PermsByRoleForRbacDetectionRulePermissionTypePermissionsByRole.from_dict(starting_permissions),
    )


class DetectionRule():
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client


    def list_all(self, tenant_id: str) -> list[DetectionRuleSummary]:
        req_body = ListDetectionRulesRequestData(
            tenant_id=tenant_id
        )

        resp = list_detection_rules.sync_detailed(
            client=self._client,
            body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rules


    def create(
        self,
        tenant_id: str,
        name: str,
        description: str,
        time_range_s: int,
        run_frequency_s: int,
        enabled: bool,
        severity: DetectionSeverity,
        query_text: str,
        event_sink_ids: list[str],
        starting_permissions: Optional[PermsByRoleForRbacDetectionRulePermissionType] | Unset = UNSET,
        sync_key: Optional[str] | Unset = UNSET,
    ) -> DetectionRuleJson:
        req_body = CreateDetectionRuleRequestData(
            tenant_id = tenant_id,
            name = name,
            description = description,
            time_range_s = time_range_s,
            run_frequency_s = run_frequency_s,
            enabled = enabled,
            severity = severity.value,
            query_text = query_text,
            event_sink_ids = event_sink_ids,
            starting_permissions = starting_permissions,
            sync_key = sync_key,
        )

        resp = create_detection_rule.sync_detailed(
            client=self._client,
            body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule


    def get(self, detection_rule_id: str) -> DetectionRuleJson:
        resp = get_detection_rule.sync_detailed(
            detection_rule_id,
            client=self._client
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule


    def update(
        self,
        detection_rule_id: str,
        name: str | Unset = UNSET,
        description: str | Unset = UNSET,
        time_range_s: int | Unset = UNSET,
        run_frequency_s: int | Unset = UNSET,
        enabled: bool | Unset = UNSET,
        severity: DetectionSeverity | Unset = UNSET,
        query_text: str | Unset = UNSET,
        event_sink_ids: list[str] | Unset = UNSET,
        sync_key: Optional[str] | Unset = UNSET,
    ) -> DetectionRuleJson:
        req_body = UpdateDetectionRuleRequestData(
            id=detection_rule_id,
            name=name,
            description=description,
            time_range_s=time_range_s,
            run_frequency_s=run_frequency_s,
            enabled=enabled,
            severity=severity,
            query_text=query_text,
            event_sink_ids=event_sink_ids,
            sync_key=sync_key
        )

        resp = update_detection_rule.sync_detailed(
            detection_rule_id,
            client=self._client,
            body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule


    def delete(self, detection_rule_id: str) -> DeleteDetectionRuleResponseData:
        resp = delete_detection_rule.sync_detailed(
            detection_rule_id,
            client=self._client
        )

        return get_body_and_handle_err(resp)


class AsyncDetectionRule():
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client


    async def list_all(self, tenant_id: str) -> list[DetectionRuleSummary]:
        req_body = ListDetectionRulesRequestData(
            tenant_id=tenant_id
        )

        resp = await list_detection_rules.asyncio_detailed(
            client=self._client,
            body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rules


    async def create(
        self,
        tenant_id: str,
        name: str,
        description: str,
        time_range_s: int,
        run_frequency_s: int,
        enabled: bool,
        severity: DetectionSeverity,
        query_text: str,
        event_sink_ids: list[str],
        sync_key: Optional[str] | Unset = UNSET,
    ) -> DetectionRuleJson:
        req_body = CreateDetectionRuleRequestData(
            tenant_id = tenant_id,
            name = name,
            description = description,
            time_range_s = time_range_s,
            run_frequency_s = run_frequency_s,
            enabled = enabled,
            severity = severity.value,
            query_text = query_text,
            event_sink_ids = event_sink_ids,
            sync_key = sync_key,
        )

        resp = await create_detection_rule.asyncio_detailed(
            client=self._client,
            body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule


    async def get(self, detection_rule_id: str) -> DetectionRuleJson:
        resp = await get_detection_rule.asyncio_detailed(
            detection_rule_id,
            client=self._client
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule


    async def update(
        self,
        detection_rule_id: str,
        name: str | Unset = UNSET,
        description: str | Unset = UNSET,
        time_range_s: int | Unset = UNSET,
        run_frequency_s: int | Unset = UNSET,
        enabled: bool | Unset = UNSET,
        severity: DetectionSeverity | Unset = UNSET,
        query_text: str | Unset = UNSET,
        event_sink_ids: list[str] | Unset = UNSET,
        sync_key: Optional[str] | Unset = UNSET,
    ) -> DetectionRuleJson:
        req_body = UpdateDetectionRuleRequestData(
            id=detection_rule_id,
            name=name,
            description=description,
            time_range_s=time_range_s,
            run_frequency_s=run_frequency_s,
            enabled=enabled,
            severity=severity,
            query_text=query_text,
            event_sink_ids=event_sink_ids,
            sync_key=sync_key
        )

        resp = await update_detection_rule.asyncio_detailed(
            detection_rule_id,
            client=self._client,
            body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule


    async def delete(self, detection_rule_id: str) -> DeleteDetectionRuleResponseData:
        resp = await delete_detection_rule.asyncio_detailed(
            detection_rule_id,
            client=self._client
        )

        return get_body_and_handle_err(resp)
