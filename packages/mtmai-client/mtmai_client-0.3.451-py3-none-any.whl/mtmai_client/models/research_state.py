from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.editor import Editor
    from ..models.interview_state import InterviewState
    from ..models.outline import Outline
    from ..models.wiki_section import WikiSection


T = TypeVar("T", bound="ResearchState")


@_attrs_define
class ResearchState:
    """
    Attributes:
        topic (str):
        outline (Outline):
        editors (List['Editor']):
        interview_results (List['InterviewState']):
        sections (List['WikiSection']):
        article (str):
    """

    topic: str
    outline: "Outline"
    editors: List["Editor"]
    interview_results: List["InterviewState"]
    sections: List["WikiSection"]
    article: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        topic = self.topic

        outline = self.outline.to_dict()

        editors = []
        for editors_item_data in self.editors:
            editors_item = editors_item_data.to_dict()
            editors.append(editors_item)

        interview_results = []
        for interview_results_item_data in self.interview_results:
            interview_results_item = interview_results_item_data.to_dict()
            interview_results.append(interview_results_item)

        sections = []
        for sections_item_data in self.sections:
            sections_item = sections_item_data.to_dict()
            sections.append(sections_item)

        article = self.article

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "topic": topic,
                "outline": outline,
                "editors": editors,
                "interview_results": interview_results,
                "sections": sections,
                "article": article,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.editor import Editor
        from ..models.interview_state import InterviewState
        from ..models.outline import Outline
        from ..models.wiki_section import WikiSection

        d = src_dict.copy()
        topic = d.pop("topic")

        outline = Outline.from_dict(d.pop("outline"))

        editors = []
        _editors = d.pop("editors")
        for editors_item_data in _editors:
            editors_item = Editor.from_dict(editors_item_data)

            editors.append(editors_item)

        interview_results = []
        _interview_results = d.pop("interview_results")
        for interview_results_item_data in _interview_results:
            interview_results_item = InterviewState.from_dict(interview_results_item_data)

            interview_results.append(interview_results_item)

        sections = []
        _sections = d.pop("sections")
        for sections_item_data in _sections:
            sections_item = WikiSection.from_dict(sections_item_data)

            sections.append(sections_item)

        article = d.pop("article")

        research_state = cls(
            topic=topic,
            outline=outline,
            editors=editors,
            interview_results=interview_results,
            sections=sections,
            article=article,
        )

        research_state.additional_properties = d
        return research_state

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
