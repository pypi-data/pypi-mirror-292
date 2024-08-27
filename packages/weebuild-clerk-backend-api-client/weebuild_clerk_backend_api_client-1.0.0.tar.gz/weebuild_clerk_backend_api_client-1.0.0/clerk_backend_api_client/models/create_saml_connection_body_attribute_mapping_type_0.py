from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateSAMLConnectionBodyAttributeMappingType0")


@_attrs_define
class CreateSAMLConnectionBodyAttributeMappingType0:
    """Define the attribute name mapping between Identity Provider and Clerk's user properties

    Attributes:
        user_id (Union[Unset, str]):
        email_address (Union[Unset, str]):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
    """

    user_id: Union[Unset, str] = UNSET
    email_address: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        user_id = self.user_id

        email_address = self.email_address

        first_name = self.first_name

        last_name = self.last_name

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if email_address is not UNSET:
            field_dict["email_address"] = email_address
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        user_id = d.pop("user_id", UNSET)

        email_address = d.pop("email_address", UNSET)

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        create_saml_connection_body_attribute_mapping_type_0 = cls(
            user_id=user_id,
            email_address=email_address,
            first_name=first_name,
            last_name=last_name,
        )

        return create_saml_connection_body_attribute_mapping_type_0
