import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Subdomain")


@_attrs_define
class Subdomain:
    """
    Attributes:
        id (int):
        name (str):
        created_at (Union[None, datetime.datetime]):
        updated_at (Union[None, datetime.datetime]):
        enabled (Union[Unset, bool]):
        is_online (Union[None, Unset, bool]):
        is_resolvable (Union[None, Unset, bool]):
        is_private (Union[None, Unset, bool]):
        is_wildcard (Union[None, Unset, bool]):
        program (Union[None, Unset, int]):
    """

    id: int
    name: str
    created_at: Union[None, datetime.datetime]
    updated_at: Union[None, datetime.datetime]
    enabled: Union[Unset, bool] = UNSET
    is_online: Union[None, Unset, bool] = UNSET
    is_resolvable: Union[None, Unset, bool] = UNSET
    is_private: Union[None, Unset, bool] = UNSET
    is_wildcard: Union[None, Unset, bool] = UNSET
    program: Union[None, Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        created_at: Union[None, str]
        if isinstance(self.created_at, datetime.datetime):
            created_at = self.created_at.isoformat()
        else:
            created_at = self.created_at

        updated_at: Union[None, str]
        if isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        enabled = self.enabled

        is_online: Union[None, Unset, bool]
        if isinstance(self.is_online, Unset):
            is_online = UNSET
        else:
            is_online = self.is_online

        is_resolvable: Union[None, Unset, bool]
        if isinstance(self.is_resolvable, Unset):
            is_resolvable = UNSET
        else:
            is_resolvable = self.is_resolvable

        is_private: Union[None, Unset, bool]
        if isinstance(self.is_private, Unset):
            is_private = UNSET
        else:
            is_private = self.is_private

        is_wildcard: Union[None, Unset, bool]
        if isinstance(self.is_wildcard, Unset):
            is_wildcard = UNSET
        else:
            is_wildcard = self.is_wildcard

        program: Union[None, Unset, int]
        if isinstance(self.program, Unset):
            program = UNSET
        else:
            program = self.program

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if is_online is not UNSET:
            field_dict["is_online"] = is_online
        if is_resolvable is not UNSET:
            field_dict["is_resolvable"] = is_resolvable
        if is_private is not UNSET:
            field_dict["is_private"] = is_private
        if is_wildcard is not UNSET:
            field_dict["is_wildcard"] = is_wildcard
        if program is not UNSET:
            field_dict["program"] = program

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        def _parse_created_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                created_at_type_0 = isoparse(data)

                return created_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        created_at = _parse_created_at(d.pop("created_at"))

        def _parse_updated_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        updated_at = _parse_updated_at(d.pop("updated_at"))

        enabled = d.pop("enabled", UNSET)

        def _parse_is_online(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_online = _parse_is_online(d.pop("is_online", UNSET))

        def _parse_is_resolvable(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_resolvable = _parse_is_resolvable(d.pop("is_resolvable", UNSET))

        def _parse_is_private(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_private = _parse_is_private(d.pop("is_private", UNSET))

        def _parse_is_wildcard(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_wildcard = _parse_is_wildcard(d.pop("is_wildcard", UNSET))

        def _parse_program(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        program = _parse_program(d.pop("program", UNSET))

        subdomain = cls(
            id=id,
            name=name,
            created_at=created_at,
            updated_at=updated_at,
            enabled=enabled,
            is_online=is_online,
            is_resolvable=is_resolvable,
            is_private=is_private,
            is_wildcard=is_wildcard,
            program=program,
        )

        subdomain.additional_properties = d
        return subdomain

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
