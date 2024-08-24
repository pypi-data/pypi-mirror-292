from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Knownledge")


@_attrs_define
class Knownledge:
    """
    Attributes:
        wid (str):
        title (str):
        id (Union[Unset, int]):
        content (Union[Unset, str]):
    """

    wid: str
    title: str
    id: Union[Unset, int] = UNSET
    content: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        wid = self.wid

        title = self.title

        id = self.id

        content = self.content

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "wid": wid,
                "title": title,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        wid = d.pop("wid")

        title = d.pop("title")

        id = d.pop("id", UNSET)

        content = d.pop("content", UNSET)

        knownledge = cls(
            wid=wid,
            title=title,
            id=id,
            content=content,
        )

        knownledge.additional_properties = d
        return knownledge

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
