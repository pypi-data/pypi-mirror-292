from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_mock import (
        GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemMock,
    )
    from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_retry import (
        GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemRetry,
    )
    from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_sleep_type_0 import (
        GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType0,
    )
    from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_sleep_type_1 import (
        GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType1,
    )
    from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_stop_after_all_iters_if import (
        GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemStopAfterAllItersIf,
    )
    from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_stop_after_if import (
        GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemStopAfterIf,
    )
    from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_suspend import (
        GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSuspend,
    )


T = TypeVar("T", bound="GetSuspendedJobFlowResponse200JobType1RawFlowModulesItem")


@_attrs_define
class GetSuspendedJobFlowResponse200JobType1RawFlowModulesItem:
    """
    Attributes:
        id (str):
        value (Any):
        stop_after_if (Union[Unset, GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemStopAfterIf]):
        stop_after_all_iters_if (Union[Unset,
            GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemStopAfterAllItersIf]):
        sleep (Union['GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType0',
            'GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType1', Unset]):
        cache_ttl (Union[Unset, float]):
        timeout (Union[Unset, float]):
        delete_after_use (Union[Unset, bool]):
        summary (Union[Unset, str]):
        mock (Union[Unset, GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemMock]):
        suspend (Union[Unset, GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSuspend]):
        priority (Union[Unset, float]):
        continue_on_error (Union[Unset, bool]):
        retry (Union[Unset, GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemRetry]):
    """

    id: str
    value: Any
    stop_after_if: Union[Unset, "GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemStopAfterIf"] = UNSET
    stop_after_all_iters_if: Union[
        Unset, "GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemStopAfterAllItersIf"
    ] = UNSET
    sleep: Union[
        "GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType0",
        "GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType1",
        Unset,
    ] = UNSET
    cache_ttl: Union[Unset, float] = UNSET
    timeout: Union[Unset, float] = UNSET
    delete_after_use: Union[Unset, bool] = UNSET
    summary: Union[Unset, str] = UNSET
    mock: Union[Unset, "GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemMock"] = UNSET
    suspend: Union[Unset, "GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSuspend"] = UNSET
    priority: Union[Unset, float] = UNSET
    continue_on_error: Union[Unset, bool] = UNSET
    retry: Union[Unset, "GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemRetry"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_sleep_type_0 import (
            GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType0,
        )

        id = self.id
        value = self.value
        stop_after_if: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.stop_after_if, Unset):
            stop_after_if = self.stop_after_if.to_dict()

        stop_after_all_iters_if: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.stop_after_all_iters_if, Unset):
            stop_after_all_iters_if = self.stop_after_all_iters_if.to_dict()

        sleep: Union[Dict[str, Any], Unset]
        if isinstance(self.sleep, Unset):
            sleep = UNSET

        elif isinstance(self.sleep, GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType0):
            sleep = UNSET
            if not isinstance(self.sleep, Unset):
                sleep = self.sleep.to_dict()

        else:
            sleep = UNSET
            if not isinstance(self.sleep, Unset):
                sleep = self.sleep.to_dict()

        cache_ttl = self.cache_ttl
        timeout = self.timeout
        delete_after_use = self.delete_after_use
        summary = self.summary
        mock: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.mock, Unset):
            mock = self.mock.to_dict()

        suspend: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.suspend, Unset):
            suspend = self.suspend.to_dict()

        priority = self.priority
        continue_on_error = self.continue_on_error
        retry: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.retry, Unset):
            retry = self.retry.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "value": value,
            }
        )
        if stop_after_if is not UNSET:
            field_dict["stop_after_if"] = stop_after_if
        if stop_after_all_iters_if is not UNSET:
            field_dict["stop_after_all_iters_if"] = stop_after_all_iters_if
        if sleep is not UNSET:
            field_dict["sleep"] = sleep
        if cache_ttl is not UNSET:
            field_dict["cache_ttl"] = cache_ttl
        if timeout is not UNSET:
            field_dict["timeout"] = timeout
        if delete_after_use is not UNSET:
            field_dict["delete_after_use"] = delete_after_use
        if summary is not UNSET:
            field_dict["summary"] = summary
        if mock is not UNSET:
            field_dict["mock"] = mock
        if suspend is not UNSET:
            field_dict["suspend"] = suspend
        if priority is not UNSET:
            field_dict["priority"] = priority
        if continue_on_error is not UNSET:
            field_dict["continue_on_error"] = continue_on_error
        if retry is not UNSET:
            field_dict["retry"] = retry

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_mock import (
            GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemMock,
        )
        from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_retry import (
            GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemRetry,
        )
        from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_sleep_type_0 import (
            GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType0,
        )
        from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_sleep_type_1 import (
            GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType1,
        )
        from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_stop_after_all_iters_if import (
            GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemStopAfterAllItersIf,
        )
        from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_stop_after_if import (
            GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemStopAfterIf,
        )
        from ..models.get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item_suspend import (
            GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSuspend,
        )

        d = src_dict.copy()
        id = d.pop("id")

        value = d.pop("value")

        _stop_after_if = d.pop("stop_after_if", UNSET)
        stop_after_if: Union[Unset, GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemStopAfterIf]
        if isinstance(_stop_after_if, Unset):
            stop_after_if = UNSET
        else:
            stop_after_if = GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemStopAfterIf.from_dict(
                _stop_after_if
            )

        _stop_after_all_iters_if = d.pop("stop_after_all_iters_if", UNSET)
        stop_after_all_iters_if: Union[
            Unset, GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemStopAfterAllItersIf
        ]
        if isinstance(_stop_after_all_iters_if, Unset):
            stop_after_all_iters_if = UNSET
        else:
            stop_after_all_iters_if = (
                GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemStopAfterAllItersIf.from_dict(
                    _stop_after_all_iters_if
                )
            )

        def _parse_sleep(
            data: object,
        ) -> Union[
            "GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType0",
            "GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType1",
            Unset,
        ]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _sleep_type_0 = data
                sleep_type_0: Union[Unset, GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType0]
                if isinstance(_sleep_type_0, Unset):
                    sleep_type_0 = UNSET
                else:
                    sleep_type_0 = GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType0.from_dict(
                        _sleep_type_0
                    )

                return sleep_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            _sleep_type_1 = data
            sleep_type_1: Union[Unset, GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType1]
            if isinstance(_sleep_type_1, Unset):
                sleep_type_1 = UNSET
            else:
                sleep_type_1 = GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSleepType1.from_dict(
                    _sleep_type_1
                )

            return sleep_type_1

        sleep = _parse_sleep(d.pop("sleep", UNSET))

        cache_ttl = d.pop("cache_ttl", UNSET)

        timeout = d.pop("timeout", UNSET)

        delete_after_use = d.pop("delete_after_use", UNSET)

        summary = d.pop("summary", UNSET)

        _mock = d.pop("mock", UNSET)
        mock: Union[Unset, GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemMock]
        if isinstance(_mock, Unset):
            mock = UNSET
        else:
            mock = GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemMock.from_dict(_mock)

        _suspend = d.pop("suspend", UNSET)
        suspend: Union[Unset, GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSuspend]
        if isinstance(_suspend, Unset):
            suspend = UNSET
        else:
            suspend = GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemSuspend.from_dict(_suspend)

        priority = d.pop("priority", UNSET)

        continue_on_error = d.pop("continue_on_error", UNSET)

        _retry = d.pop("retry", UNSET)
        retry: Union[Unset, GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemRetry]
        if isinstance(_retry, Unset):
            retry = UNSET
        else:
            retry = GetSuspendedJobFlowResponse200JobType1RawFlowModulesItemRetry.from_dict(_retry)

        get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item = cls(
            id=id,
            value=value,
            stop_after_if=stop_after_if,
            stop_after_all_iters_if=stop_after_all_iters_if,
            sleep=sleep,
            cache_ttl=cache_ttl,
            timeout=timeout,
            delete_after_use=delete_after_use,
            summary=summary,
            mock=mock,
            suspend=suspend,
            priority=priority,
            continue_on_error=continue_on_error,
            retry=retry,
        )

        get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item.additional_properties = d
        return get_suspended_job_flow_response_200_job_type_1_raw_flow_modules_item

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
