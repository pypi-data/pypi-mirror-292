from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrganizationMembershipPublicUserData")


@_attrs_define
class OrganizationMembershipPublicUserData:
    """
    Attributes:
        user_id (Union[Unset, str]):
        first_name (Union[None, Unset, str]):
        last_name (Union[None, Unset, str]):
        profile_image_url (Union[None, Unset, str]):
        image_url (Union[Unset, str]):
        has_image (Union[Unset, bool]):
        identifier (Union[None, Unset, str]):
    """

    user_id: Union[Unset, str] = UNSET
    first_name: Union[None, Unset, str] = UNSET
    last_name: Union[None, Unset, str] = UNSET
    profile_image_url: Union[None, Unset, str] = UNSET
    image_url: Union[Unset, str] = UNSET
    has_image: Union[Unset, bool] = UNSET
    identifier: Union[None, Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        user_id = self.user_id

        first_name: Union[None, Unset, str]
        if isinstance(self.first_name, Unset):
            first_name = UNSET
        else:
            first_name = self.first_name

        last_name: Union[None, Unset, str]
        if isinstance(self.last_name, Unset):
            last_name = UNSET
        else:
            last_name = self.last_name

        profile_image_url: Union[None, Unset, str]
        if isinstance(self.profile_image_url, Unset):
            profile_image_url = UNSET
        else:
            profile_image_url = self.profile_image_url

        image_url = self.image_url

        has_image = self.has_image

        identifier: Union[None, Unset, str]
        if isinstance(self.identifier, Unset):
            identifier = UNSET
        else:
            identifier = self.identifier

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if profile_image_url is not UNSET:
            field_dict["profile_image_url"] = profile_image_url
        if image_url is not UNSET:
            field_dict["image_url"] = image_url
        if has_image is not UNSET:
            field_dict["has_image"] = has_image
        if identifier is not UNSET:
            field_dict["identifier"] = identifier

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        user_id = d.pop("user_id", UNSET)

        def _parse_first_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        first_name = _parse_first_name(d.pop("first_name", UNSET))

        def _parse_last_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        last_name = _parse_last_name(d.pop("last_name", UNSET))

        def _parse_profile_image_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        profile_image_url = _parse_profile_image_url(d.pop("profile_image_url", UNSET))

        image_url = d.pop("image_url", UNSET)

        has_image = d.pop("has_image", UNSET)

        def _parse_identifier(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        identifier = _parse_identifier(d.pop("identifier", UNSET))

        organization_membership_public_user_data = cls(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            profile_image_url=profile_image_url,
            image_url=image_url,
            has_image=has_image,
            identifier=identifier,
        )

        return organization_membership_public_user_data
