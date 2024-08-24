from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Editor")


@_attrs_define
class Editor:
    """
    Attributes:
        affiliation (str): Primary affiliation of the editor.
        name (str): Name of the editor.
        role (str): Role of the editor in the context of the topic.
        description (str): Description of the editor's focus, concerns, and motives.
    """

    affiliation: str
    name: str
    role: str
    description: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        affiliation = self.affiliation

        name = self.name

        role = self.role

        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "affiliation": affiliation,
                "name": name,
                "role": role,
                "description": description,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        affiliation = d.pop("affiliation")

        name = d.pop("name")

        role = d.pop("role")

        description = d.pop("description")

        editor = cls(
            affiliation=affiliation,
            name=name,
            role=role,
            description=description,
        )

        editor.additional_properties = d
        return editor

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
