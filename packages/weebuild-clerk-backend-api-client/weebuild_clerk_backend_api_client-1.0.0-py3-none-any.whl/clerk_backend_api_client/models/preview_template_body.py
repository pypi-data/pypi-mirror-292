from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PreviewTemplateBody")


@_attrs_define
class PreviewTemplateBody:
    """
    Attributes:
        subject (Union[None, Unset, str]): The email subject.
            Applicable only to email templates.
        body (Union[Unset, str]): The template body before variable interpolation
        from_email_name (Union[Unset, str]): The local part of the From email address that will be used for emails.
            For example, in the address 'hello@example.com', the local part is 'hello'.
            Applicable only to email templates.
        reply_to_email_name (Union[Unset, str]): The local part of the Reply To email address that will be used for
            emails.
            For example, in the address 'hello@example.com', the local part is 'hello'.
            Applicable only to email templates.
    """

    subject: Union[None, Unset, str] = UNSET
    body: Union[Unset, str] = UNSET
    from_email_name: Union[Unset, str] = UNSET
    reply_to_email_name: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        subject: Union[None, Unset, str]
        if isinstance(self.subject, Unset):
            subject = UNSET
        else:
            subject = self.subject

        body = self.body

        from_email_name = self.from_email_name

        reply_to_email_name = self.reply_to_email_name

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if subject is not UNSET:
            field_dict["subject"] = subject
        if body is not UNSET:
            field_dict["body"] = body
        if from_email_name is not UNSET:
            field_dict["from_email_name"] = from_email_name
        if reply_to_email_name is not UNSET:
            field_dict["reply_to_email_name"] = reply_to_email_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_subject(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        subject = _parse_subject(d.pop("subject", UNSET))

        body = d.pop("body", UNSET)

        from_email_name = d.pop("from_email_name", UNSET)

        reply_to_email_name = d.pop("reply_to_email_name", UNSET)

        preview_template_body = cls(
            subject=subject,
            body=body,
            from_email_name=from_email_name,
            reply_to_email_name=reply_to_email_name,
        )

        return preview_template_body
