import datetime
from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse


T = TypeVar("T", bound="Group")


@_attrs_define
class Group:
    """Group model

    Attributes:
        created_on (datetime.datetime):
        id (str):
        name (str):
    """

    created_on: datetime.datetime
    id: str
    name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        created_on = self.created_on.isoformat()
        id = self.id
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "createdOn": created_on,
                "id": id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Group` from a dict"""
        d = src_dict.copy()
        created_on = isoparse(d.pop("createdOn"))

        id = d.pop("id")

        name = d.pop("name")

        group = cls(
            created_on=created_on,
            id=id,
            name=name,
        )

        return group
