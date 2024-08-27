from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

from ..models.redirect_url_object import RedirectURLObject

T = TypeVar("T", bound="RedirectURL")


@_attrs_define
class RedirectURL:
    """
    Attributes:
        object_ (RedirectURLObject):
        id (str):
        url (str):
        created_at (int): Unix timestamp of creation.
        updated_at (int): Unix timestamp of last update.
    """

    object_: RedirectURLObject
    id: str
    url: str
    created_at: int
    updated_at: int

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_.value

        id = self.id

        url = self.url

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "object": object_,
                "id": id,
                "url": url,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        object_ = RedirectURLObject(d.pop("object"))

        id = d.pop("id")

        url = d.pop("url")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        redirect_url = cls(
            object_=object_,
            id=id,
            url=url,
            created_at=created_at,
            updated_at=updated_at,
        )

        return redirect_url
