from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..models.email_address_object import EmailAddressObject
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.admin import Admin
    from ..models.identification_link import IdentificationLink
    from ..models.oauth import Oauth
    from ..models.otp import OTP


T = TypeVar("T", bound="EmailAddress")


@_attrs_define
class EmailAddress:
    """
    Attributes:
        object_ (EmailAddressObject): String representing the object's type. Objects of the same type share the same
            value.
        email_address (str):
        reserved (bool):
        verification (Union['Admin', 'OTP', 'Oauth']):
        linked_to (List['IdentificationLink']):
        created_at (int): Unix timestamp of creation
        updated_at (int): Unix timestamp of creation
        id (Union[Unset, str]):
    """

    object_: EmailAddressObject
    email_address: str
    reserved: bool
    verification: Union["Admin", "OTP", "Oauth"]
    linked_to: List["IdentificationLink"]
    created_at: int
    updated_at: int
    id: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        from ..models.admin import Admin
        from ..models.oauth import Oauth
        from ..models.otp import OTP

        object_ = self.object_.value

        email_address = self.email_address

        reserved = self.reserved

        verification: Dict[str, Any]
        if isinstance(self.verification, OTP):
            verification = self.verification.to_dict()
        elif isinstance(self.verification, Admin):
            verification = self.verification.to_dict()
        elif isinstance(self.verification, Oauth):
            verification = self.verification.to_dict()
        elif isinstance(self.verification, OTP):
            verification = self.verification.to_dict()
        elif isinstance(self.verification, Admin):
            verification = self.verification.to_dict()
        elif isinstance(self.verification, Oauth):
            verification = self.verification.to_dict()
        elif isinstance(self.verification, OTP):
            verification = self.verification.to_dict()
        elif isinstance(self.verification, Admin):
            verification = self.verification.to_dict()
        else:
            verification = self.verification.to_dict()

        linked_to = []
        for linked_to_item_data in self.linked_to:
            linked_to_item = linked_to_item_data.to_dict()
            linked_to.append(linked_to_item)

        created_at = self.created_at

        updated_at = self.updated_at

        id = self.id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "object": object_,
                "email_address": email_address,
                "reserved": reserved,
                "verification": verification,
                "linked_to": linked_to,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.admin import Admin
        from ..models.identification_link import IdentificationLink
        from ..models.oauth import Oauth
        from ..models.otp import OTP

        d = src_dict.copy()
        object_ = EmailAddressObject(d.pop("object"))

        email_address = d.pop("email_address")

        reserved = d.pop("reserved")

        def _parse_verification(data: object) -> Union["Admin", "OTP", "Oauth"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                verification_type_0 = OTP.from_dict(data)

                return verification_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                verification_type_1 = Admin.from_dict(data)

                return verification_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                verification_type_2 = Oauth.from_dict(data)

                return verification_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                verification_type_3_type_0 = OTP.from_dict(data)

                return verification_type_3_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                verification_type_3_type_1 = Admin.from_dict(data)

                return verification_type_3_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                verification_type_3_type_2 = Oauth.from_dict(data)

                return verification_type_3_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                verification_type_4_type_0 = OTP.from_dict(data)

                return verification_type_4_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                verification_type_4_type_1 = Admin.from_dict(data)

                return verification_type_4_type_1
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            verification_type_4_type_2 = Oauth.from_dict(data)

            return verification_type_4_type_2

        verification = _parse_verification(d.pop("verification"))

        linked_to = []
        _linked_to = d.pop("linked_to")
        for linked_to_item_data in _linked_to:
            linked_to_item = IdentificationLink.from_dict(linked_to_item_data)

            linked_to.append(linked_to_item)

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        id = d.pop("id", UNSET)

        email_address = cls(
            object_=object_,
            email_address=email_address,
            reserved=reserved,
            verification=verification,
            linked_to=linked_to,
            created_at=created_at,
            updated_at=updated_at,
            id=id,
        )

        return email_address
