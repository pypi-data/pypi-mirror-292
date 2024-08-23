from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetQueueCountResponse200")


@_attrs_define
class GetQueueCountResponse200:
    """
    Attributes:
        database_length (int):
        suspended (Union[Unset, int]):
    """

    database_length: int
    suspended: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        database_length = self.database_length
        suspended = self.suspended

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "database_length": database_length,
            }
        )
        if suspended is not UNSET:
            field_dict["suspended"] = suspended

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        database_length = d.pop("database_length")

        suspended = d.pop("suspended", UNSET)

        get_queue_count_response_200 = cls(
            database_length=database_length,
            suspended=suspended,
        )

        get_queue_count_response_200.additional_properties = d
        return get_queue_count_response_200

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
