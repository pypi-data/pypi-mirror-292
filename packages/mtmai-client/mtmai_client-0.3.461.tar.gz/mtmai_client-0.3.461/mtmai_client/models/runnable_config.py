from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.runnable_config_configurable import RunnableConfigConfigurable
    from ..models.runnable_config_metadata import RunnableConfigMetadata


T = TypeVar("T", bound="RunnableConfig")


@_attrs_define
class RunnableConfig:
    """Configuration for a Runnable.

    Attributes:
        tags (Union[Unset, List[str]]):
        metadata (Union[Unset, RunnableConfigMetadata]):
        callbacks (Union[Any, List[Any], None, Unset]):
        run_name (Union[Unset, str]):
        max_concurrency (Union[None, Unset, int]):
        recursion_limit (Union[Unset, int]):
        configurable (Union[Unset, RunnableConfigConfigurable]):
        run_id (Union[None, Unset, str]):
    """

    tags: Union[Unset, List[str]] = UNSET
    metadata: Union[Unset, "RunnableConfigMetadata"] = UNSET
    callbacks: Union[Any, List[Any], None, Unset] = UNSET
    run_name: Union[Unset, str] = UNSET
    max_concurrency: Union[None, Unset, int] = UNSET
    recursion_limit: Union[Unset, int] = UNSET
    configurable: Union[Unset, "RunnableConfigConfigurable"] = UNSET
    run_id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        tags: Union[Unset, List[str]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        callbacks: Union[Any, List[Any], None, Unset]
        if isinstance(self.callbacks, Unset):
            callbacks = UNSET
        elif isinstance(self.callbacks, list):
            callbacks = self.callbacks

        else:
            callbacks = self.callbacks

        run_name = self.run_name

        max_concurrency: Union[None, Unset, int]
        if isinstance(self.max_concurrency, Unset):
            max_concurrency = UNSET
        else:
            max_concurrency = self.max_concurrency

        recursion_limit = self.recursion_limit

        configurable: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.configurable, Unset):
            configurable = self.configurable.to_dict()

        run_id: Union[None, Unset, str]
        if isinstance(self.run_id, Unset):
            run_id = UNSET
        else:
            run_id = self.run_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tags is not UNSET:
            field_dict["tags"] = tags
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if callbacks is not UNSET:
            field_dict["callbacks"] = callbacks
        if run_name is not UNSET:
            field_dict["run_name"] = run_name
        if max_concurrency is not UNSET:
            field_dict["max_concurrency"] = max_concurrency
        if recursion_limit is not UNSET:
            field_dict["recursion_limit"] = recursion_limit
        if configurable is not UNSET:
            field_dict["configurable"] = configurable
        if run_id is not UNSET:
            field_dict["run_id"] = run_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.runnable_config_configurable import RunnableConfigConfigurable
        from ..models.runnable_config_metadata import RunnableConfigMetadata

        d = src_dict.copy()
        tags = cast(List[str], d.pop("tags", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, RunnableConfigMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = RunnableConfigMetadata.from_dict(_metadata)

        def _parse_callbacks(data: object) -> Union[Any, List[Any], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                callbacks_type_0 = cast(List[Any], data)

                return callbacks_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Any, List[Any], None, Unset], data)

        callbacks = _parse_callbacks(d.pop("callbacks", UNSET))

        run_name = d.pop("run_name", UNSET)

        def _parse_max_concurrency(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_concurrency = _parse_max_concurrency(d.pop("max_concurrency", UNSET))

        recursion_limit = d.pop("recursion_limit", UNSET)

        _configurable = d.pop("configurable", UNSET)
        configurable: Union[Unset, RunnableConfigConfigurable]
        if isinstance(_configurable, Unset):
            configurable = UNSET
        else:
            configurable = RunnableConfigConfigurable.from_dict(_configurable)

        def _parse_run_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        run_id = _parse_run_id(d.pop("run_id", UNSET))

        runnable_config = cls(
            tags=tags,
            metadata=metadata,
            callbacks=callbacks,
            run_name=run_name,
            max_concurrency=max_concurrency,
            recursion_limit=recursion_limit,
            configurable=configurable,
            run_id=run_id,
        )

        runnable_config.additional_properties = d
        return runnable_config

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
