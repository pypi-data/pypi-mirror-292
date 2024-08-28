from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.subsection import Subsection


T = TypeVar("T", bound="WikiSection")


@_attrs_define
class WikiSection:
    """
    Attributes:
        section_title (str):
        content (str):
        subsections (Union[List['Subsection'], None, Unset]):
        citations (Union[Unset, List[str]]):
    """

    section_title: str
    content: str
    subsections: Union[List["Subsection"], None, Unset] = UNSET
    citations: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        section_title = self.section_title

        content = self.content

        subsections: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.subsections, Unset):
            subsections = UNSET
        elif isinstance(self.subsections, list):
            subsections = []
            for subsections_type_0_item_data in self.subsections:
                subsections_type_0_item = subsections_type_0_item_data.to_dict()
                subsections.append(subsections_type_0_item)

        else:
            subsections = self.subsections

        citations: Union[Unset, List[str]] = UNSET
        if not isinstance(self.citations, Unset):
            citations = self.citations

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "section_title": section_title,
                "content": content,
            }
        )
        if subsections is not UNSET:
            field_dict["subsections"] = subsections
        if citations is not UNSET:
            field_dict["citations"] = citations

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.subsection import Subsection

        d = src_dict.copy()
        section_title = d.pop("section_title")

        content = d.pop("content")

        def _parse_subsections(data: object) -> Union[List["Subsection"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                subsections_type_0 = []
                _subsections_type_0 = data
                for subsections_type_0_item_data in _subsections_type_0:
                    subsections_type_0_item = Subsection.from_dict(subsections_type_0_item_data)

                    subsections_type_0.append(subsections_type_0_item)

                return subsections_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["Subsection"], None, Unset], data)

        subsections = _parse_subsections(d.pop("subsections", UNSET))

        citations = cast(List[str], d.pop("citations", UNSET))

        wiki_section = cls(
            section_title=section_title,
            content=content,
            subsections=subsections,
            citations=citations,
        )

        wiki_section.additional_properties = d
        return wiki_section

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
