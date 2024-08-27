from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.invitation_object import InvitationObject
from ..models.invitation_status import InvitationStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.invitation_public_metadata import InvitationPublicMetadata


T = TypeVar("T", bound="Invitation")


@_attrs_define
class Invitation:
    """
    Attributes:
        object_ (InvitationObject):
        id (str):
        email_address (str):
        status (InvitationStatus):  Example: pending.
        created_at (int): Unix timestamp of creation.
        updated_at (int): Unix timestamp of last update.
        public_metadata (Union[Unset, InvitationPublicMetadata]):
        revoked (Union[Unset, bool]):
        url (Union[None, Unset, str]):
    """

    object_: InvitationObject
    id: str
    email_address: str
    status: InvitationStatus
    created_at: int
    updated_at: int
    public_metadata: Union[Unset, "InvitationPublicMetadata"] = UNSET
    revoked: Union[Unset, bool] = UNSET
    url: Union[None, Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_.value

        id = self.id

        email_address = self.email_address

        status = self.status.value

        created_at = self.created_at

        updated_at = self.updated_at

        public_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.public_metadata, Unset):
            public_metadata = self.public_metadata.to_dict()

        revoked = self.revoked

        url: Union[None, Unset, str]
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "object": object_,
                "id": id,
                "email_address": email_address,
                "status": status,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if public_metadata is not UNSET:
            field_dict["public_metadata"] = public_metadata
        if revoked is not UNSET:
            field_dict["revoked"] = revoked
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.invitation_public_metadata import InvitationPublicMetadata

        d = src_dict.copy()
        object_ = InvitationObject(d.pop("object"))

        id = d.pop("id")

        email_address = d.pop("email_address")

        status = InvitationStatus(d.pop("status"))

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        _public_metadata = d.pop("public_metadata", UNSET)
        public_metadata: Union[Unset, InvitationPublicMetadata]
        if isinstance(_public_metadata, Unset):
            public_metadata = UNSET
        else:
            public_metadata = InvitationPublicMetadata.from_dict(_public_metadata)

        revoked = d.pop("revoked", UNSET)

        def _parse_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        url = _parse_url(d.pop("url", UNSET))

        invitation = cls(
            object_=object_,
            id=id,
            email_address=email_address,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            public_metadata=public_metadata,
            revoked=revoked,
            url=url,
        )

        return invitation
