from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RagAddContentReq")


@_attrs_define
class RagAddContentReq:
    """
    Attributes:
        collection (Union[None, str]):
        content (str):
    """

    collection: Union[None, str]
    content: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        collection: Union[None, str]
        collection = self.collection

        content = self.content

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "collection": collection,
                "content": content,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_collection(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        collection = _parse_collection(d.pop("collection"))

        content = d.pop("content")

        rag_add_content_req = cls(
            collection=collection,
            content=content,
        )

        rag_add_content_req.additional_properties = d
        return rag_add_content_req

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
