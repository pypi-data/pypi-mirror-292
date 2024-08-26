from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.editor import Editor
    from ..models.interview_state_references_type_0 import InterviewStateReferencesType0


T = TypeVar("T", bound="InterviewState")


@_attrs_define
class InterviewState:
    """
    Attributes:
        messages (List[Any]):
        references (Union['InterviewStateReferencesType0', None]):
        editor (Union['Editor', None]):
    """

    messages: List[Any]
    references: Union["InterviewStateReferencesType0", None]
    editor: Union["Editor", None]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.editor import Editor
        from ..models.interview_state_references_type_0 import InterviewStateReferencesType0

        messages = self.messages

        references: Union[Dict[str, Any], None]
        if isinstance(self.references, InterviewStateReferencesType0):
            references = self.references.to_dict()
        else:
            references = self.references

        editor: Union[Dict[str, Any], None]
        if isinstance(self.editor, Editor):
            editor = self.editor.to_dict()
        else:
            editor = self.editor

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "messages": messages,
                "references": references,
                "editor": editor,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.editor import Editor
        from ..models.interview_state_references_type_0 import InterviewStateReferencesType0

        d = src_dict.copy()
        messages = cast(List[Any], d.pop("messages"))

        def _parse_references(data: object) -> Union["InterviewStateReferencesType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                references_type_0 = InterviewStateReferencesType0.from_dict(data)

                return references_type_0
            except:  # noqa: E722
                pass
            return cast(Union["InterviewStateReferencesType0", None], data)

        references = _parse_references(d.pop("references"))

        def _parse_editor(data: object) -> Union["Editor", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                editor_type_0 = Editor.from_dict(data)

                return editor_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Editor", None], data)

        editor = _parse_editor(d.pop("editor"))

        interview_state = cls(
            messages=messages,
            references=references,
            editor=editor,
        )

        interview_state.additional_properties = d
        return interview_state

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
