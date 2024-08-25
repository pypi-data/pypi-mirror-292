from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.section import Section


T = TypeVar("T", bound="Outline")


@_attrs_define
class Outline:
    """
    Attributes:
        page_title (str):
        sections (Union[Unset, List['Section']]):
    """

    page_title: str
    sections: Union[Unset, List["Section"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        page_title = self.page_title

        sections: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.sections, Unset):
            sections = []
            for sections_item_data in self.sections:
                sections_item = sections_item_data.to_dict()
                sections.append(sections_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "page_title": page_title,
            }
        )
        if sections is not UNSET:
            field_dict["sections"] = sections

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.section import Section

        d = src_dict.copy()
        page_title = d.pop("page_title")

        sections = []
        _sections = d.pop("sections", UNSET)
        for sections_item_data in _sections or []:
            sections_item = Section.from_dict(sections_item_data)

            sections.append(sections_item)

        outline = cls(
            page_title=page_title,
            sections=sections,
        )

        outline.additional_properties = d
        return outline

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
