from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpsertTemplateBody")


@_attrs_define
class UpsertTemplateBody:
    """
    Attributes:
        name (Union[Unset, str]): The user-friendly name of the template
        subject (Union[None, Unset, str]): The email subject.
            Applicable only to email templates.
        markup (Union[None, Unset, str]): The editor markup used to generate the body of the template
        body (Union[Unset, str]): The template body before variable interpolation
        delivered_by_clerk (Union[None, Unset, bool]): Whether Clerk should deliver emails or SMS messages based on the
            current template
        from_email_name (Union[Unset, str]): The local part of the From email address that will be used for emails.
            For example, in the address 'hello@example.com', the local part is 'hello'.
            Applicable only to email templates.
        reply_to_email_name (Union[Unset, str]): The local part of the Reply To email address that will be used for
            emails.
            For example, in the address 'hello@example.com', the local part is 'hello'.
            Applicable only to email templates.
    """

    name: Union[Unset, str] = UNSET
    subject: Union[None, Unset, str] = UNSET
    markup: Union[None, Unset, str] = UNSET
    body: Union[Unset, str] = UNSET
    delivered_by_clerk: Union[None, Unset, bool] = UNSET
    from_email_name: Union[Unset, str] = UNSET
    reply_to_email_name: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        subject: Union[None, Unset, str]
        if isinstance(self.subject, Unset):
            subject = UNSET
        else:
            subject = self.subject

        markup: Union[None, Unset, str]
        if isinstance(self.markup, Unset):
            markup = UNSET
        else:
            markup = self.markup

        body = self.body

        delivered_by_clerk: Union[None, Unset, bool]
        if isinstance(self.delivered_by_clerk, Unset):
            delivered_by_clerk = UNSET
        else:
            delivered_by_clerk = self.delivered_by_clerk

        from_email_name = self.from_email_name

        reply_to_email_name = self.reply_to_email_name

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if subject is not UNSET:
            field_dict["subject"] = subject
        if markup is not UNSET:
            field_dict["markup"] = markup
        if body is not UNSET:
            field_dict["body"] = body
        if delivered_by_clerk is not UNSET:
            field_dict["delivered_by_clerk"] = delivered_by_clerk
        if from_email_name is not UNSET:
            field_dict["from_email_name"] = from_email_name
        if reply_to_email_name is not UNSET:
            field_dict["reply_to_email_name"] = reply_to_email_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        def _parse_subject(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        subject = _parse_subject(d.pop("subject", UNSET))

        def _parse_markup(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        markup = _parse_markup(d.pop("markup", UNSET))

        body = d.pop("body", UNSET)

        def _parse_delivered_by_clerk(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        delivered_by_clerk = _parse_delivered_by_clerk(d.pop("delivered_by_clerk", UNSET))

        from_email_name = d.pop("from_email_name", UNSET)

        reply_to_email_name = d.pop("reply_to_email_name", UNSET)

        upsert_template_body = cls(
            name=name,
            subject=subject,
            markup=markup,
            body=body,
            delivered_by_clerk=delivered_by_clerk,
            from_email_name=from_email_name,
            reply_to_email_name=reply_to_email_name,
        )

        return upsert_template_body
