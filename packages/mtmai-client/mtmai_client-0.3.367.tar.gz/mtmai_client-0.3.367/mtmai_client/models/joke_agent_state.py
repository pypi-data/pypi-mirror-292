from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.joke_agent_state_messages_type_0_item import JokeAgentStateMessagesType0Item


T = TypeVar("T", bound="JokeAgentState")


@_attrs_define
class JokeAgentState:
    """
    Attributes:
        subjects (Union[List[str], None, Unset]):
        jokes (Union[List[str], None, Unset]):
        best_selected_joke (Union[None, Unset, str]):
        messages (Union[List['JokeAgentStateMessagesType0Item'], None, Unset]):
        ask_human (Union[Unset, bool]):  Default: False.
    """

    subjects: Union[List[str], None, Unset] = UNSET
    jokes: Union[List[str], None, Unset] = UNSET
    best_selected_joke: Union[None, Unset, str] = UNSET
    messages: Union[List["JokeAgentStateMessagesType0Item"], None, Unset] = UNSET
    ask_human: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        subjects: Union[List[str], None, Unset]
        if isinstance(self.subjects, Unset):
            subjects = UNSET
        elif isinstance(self.subjects, list):
            subjects = self.subjects

        else:
            subjects = self.subjects

        jokes: Union[List[str], None, Unset]
        if isinstance(self.jokes, Unset):
            jokes = UNSET
        elif isinstance(self.jokes, list):
            jokes = self.jokes

        else:
            jokes = self.jokes

        best_selected_joke: Union[None, Unset, str]
        if isinstance(self.best_selected_joke, Unset):
            best_selected_joke = UNSET
        else:
            best_selected_joke = self.best_selected_joke

        messages: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.messages, Unset):
            messages = UNSET
        elif isinstance(self.messages, list):
            messages = []
            for messages_type_0_item_data in self.messages:
                messages_type_0_item = messages_type_0_item_data.to_dict()
                messages.append(messages_type_0_item)

        else:
            messages = self.messages

        ask_human = self.ask_human

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if subjects is not UNSET:
            field_dict["subjects"] = subjects
        if jokes is not UNSET:
            field_dict["jokes"] = jokes
        if best_selected_joke is not UNSET:
            field_dict["best_selected_joke"] = best_selected_joke
        if messages is not UNSET:
            field_dict["messages"] = messages
        if ask_human is not UNSET:
            field_dict["ask_human"] = ask_human

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.joke_agent_state_messages_type_0_item import JokeAgentStateMessagesType0Item

        d = src_dict.copy()

        def _parse_subjects(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                subjects_type_0 = cast(List[str], data)

                return subjects_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        subjects = _parse_subjects(d.pop("subjects", UNSET))

        def _parse_jokes(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                jokes_type_0 = cast(List[str], data)

                return jokes_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        jokes = _parse_jokes(d.pop("jokes", UNSET))

        def _parse_best_selected_joke(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        best_selected_joke = _parse_best_selected_joke(d.pop("best_selected_joke", UNSET))

        def _parse_messages(data: object) -> Union[List["JokeAgentStateMessagesType0Item"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                messages_type_0 = []
                _messages_type_0 = data
                for messages_type_0_item_data in _messages_type_0:
                    messages_type_0_item = JokeAgentStateMessagesType0Item.from_dict(messages_type_0_item_data)

                    messages_type_0.append(messages_type_0_item)

                return messages_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["JokeAgentStateMessagesType0Item"], None, Unset], data)

        messages = _parse_messages(d.pop("messages", UNSET))

        ask_human = d.pop("ask_human", UNSET)

        joke_agent_state = cls(
            subjects=subjects,
            jokes=jokes,
            best_selected_joke=best_selected_joke,
            messages=messages,
            ask_human=ask_human,
        )

        joke_agent_state.additional_properties = d
        return joke_agent_state

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
