from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chat_message import ChatMessage


T = TypeVar("T", bound="ChatInputReq")


@_attrs_define
class ChatInputReq:
    """
    Attributes:
        messages (List['ChatMessage']):
        chat_id (Union[None, Unset, str]):
    """

    messages: List["ChatMessage"]
    chat_id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)

        chat_id: Union[None, Unset, str]
        if isinstance(self.chat_id, Unset):
            chat_id = UNSET
        else:
            chat_id = self.chat_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "messages": messages,
            }
        )
        if chat_id is not UNSET:
            field_dict["chat_id"] = chat_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.chat_message import ChatMessage

        d = src_dict.copy()
        messages = []
        _messages = d.pop("messages")
        for messages_item_data in _messages:
            messages_item = ChatMessage.from_dict(messages_item_data)

            messages.append(messages_item)

        def _parse_chat_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        chat_id = _parse_chat_id(d.pop("chat_id", UNSET))

        chat_input_req = cls(
            messages=messages,
            chat_id=chat_id,
        )

        chat_input_req.additional_properties = d
        return chat_input_req

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
