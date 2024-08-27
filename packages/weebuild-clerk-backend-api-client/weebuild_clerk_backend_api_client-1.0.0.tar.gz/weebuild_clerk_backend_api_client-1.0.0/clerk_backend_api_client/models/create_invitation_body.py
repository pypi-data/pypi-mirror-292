from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_invitation_body_public_metadata import CreateInvitationBodyPublicMetadata


T = TypeVar("T", bound="CreateInvitationBody")


@_attrs_define
class CreateInvitationBody:
    """
    Attributes:
        email_address (str): The email address the invitation will be sent to
        public_metadata (Union[Unset, CreateInvitationBodyPublicMetadata]): Metadata that will be attached to the newly
            created invitation.
            The value of this property should be a well-formed JSON object.
            Once the user accepts the invitation and signs up, these metadata will end up in the user's public metadata.
        redirect_url (Union[Unset, str]): Optional URL which specifies where to redirect the user once they click the
            invitation link.
            This is only required if you have implemented a [custom
            flow](https://clerk.com/docs/authentication/invitations#custom-flow) and you're not using Clerk Hosted Pages or
            Clerk Components.
        notify (Union[None, Unset, bool]): Optional flag which denotes whether an email invitation should be sent to the
            given email address.
            Defaults to true. Default: True.
        ignore_existing (Union[None, Unset, bool]): Whether an invitation should be created if there is already an
            existing invitation for this email address, or it's claimed by another user. Default: False.
    """

    email_address: str
    public_metadata: Union[Unset, "CreateInvitationBodyPublicMetadata"] = UNSET
    redirect_url: Union[Unset, str] = UNSET
    notify: Union[None, Unset, bool] = True
    ignore_existing: Union[None, Unset, bool] = False

    def to_dict(self) -> Dict[str, Any]:
        email_address = self.email_address

        public_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.public_metadata, Unset):
            public_metadata = self.public_metadata.to_dict()

        redirect_url = self.redirect_url

        notify: Union[None, Unset, bool]
        if isinstance(self.notify, Unset):
            notify = UNSET
        else:
            notify = self.notify

        ignore_existing: Union[None, Unset, bool]
        if isinstance(self.ignore_existing, Unset):
            ignore_existing = UNSET
        else:
            ignore_existing = self.ignore_existing

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "email_address": email_address,
            }
        )
        if public_metadata is not UNSET:
            field_dict["public_metadata"] = public_metadata
        if redirect_url is not UNSET:
            field_dict["redirect_url"] = redirect_url
        if notify is not UNSET:
            field_dict["notify"] = notify
        if ignore_existing is not UNSET:
            field_dict["ignore_existing"] = ignore_existing

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.create_invitation_body_public_metadata import CreateInvitationBodyPublicMetadata

        d = src_dict.copy()
        email_address = d.pop("email_address")

        _public_metadata = d.pop("public_metadata", UNSET)
        public_metadata: Union[Unset, CreateInvitationBodyPublicMetadata]
        if isinstance(_public_metadata, Unset):
            public_metadata = UNSET
        else:
            public_metadata = CreateInvitationBodyPublicMetadata.from_dict(_public_metadata)

        redirect_url = d.pop("redirect_url", UNSET)

        def _parse_notify(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        notify = _parse_notify(d.pop("notify", UNSET))

        def _parse_ignore_existing(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        ignore_existing = _parse_ignore_existing(d.pop("ignore_existing", UNSET))

        create_invitation_body = cls(
            email_address=email_address,
            public_metadata=public_metadata,
            redirect_url=redirect_url,
            notify=notify,
            ignore_existing=ignore_existing,
        )

        return create_invitation_body
