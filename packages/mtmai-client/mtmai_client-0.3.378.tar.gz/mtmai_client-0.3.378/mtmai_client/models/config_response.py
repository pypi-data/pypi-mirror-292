from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.sub_app import SubApp
    from ..models.sub_web import SubWeb


T = TypeVar("T", bound="ConfigResponse")


@_attrs_define
class ConfigResponse:
    """
    Attributes:
        name (str):
        subapps (List['SubApp']):
        subwebs (List['SubWeb']):
    """

    name: str
    subapps: List["SubApp"]
    subwebs: List["SubWeb"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        subapps = []
        for subapps_item_data in self.subapps:
            subapps_item = subapps_item_data.to_dict()
            subapps.append(subapps_item)

        subwebs = []
        for subwebs_item_data in self.subwebs:
            subwebs_item = subwebs_item_data.to_dict()
            subwebs.append(subwebs_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "subapps": subapps,
                "subwebs": subwebs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.sub_app import SubApp
        from ..models.sub_web import SubWeb

        d = src_dict.copy()
        name = d.pop("name")

        subapps = []
        _subapps = d.pop("subapps")
        for subapps_item_data in _subapps:
            subapps_item = SubApp.from_dict(subapps_item_data)

            subapps.append(subapps_item)

        subwebs = []
        _subwebs = d.pop("subwebs")
        for subwebs_item_data in _subwebs:
            subwebs_item = SubWeb.from_dict(subwebs_item_data)

            subwebs.append(subwebs_item)

        config_response = cls(
            name=name,
            subapps=subapps,
            subwebs=subwebs,
        )

        config_response.additional_properties = d
        return config_response

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
