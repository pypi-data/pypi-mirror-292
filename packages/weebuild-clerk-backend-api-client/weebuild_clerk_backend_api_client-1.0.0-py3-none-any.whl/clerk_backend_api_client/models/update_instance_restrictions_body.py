from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateInstanceRestrictionsBody")


@_attrs_define
class UpdateInstanceRestrictionsBody:
    """
    Attributes:
        allowlist (Union[None, Unset, bool]):
        blocklist (Union[None, Unset, bool]):
        block_email_subaddresses (Union[None, Unset, bool]):
        block_disposable_email_domains (Union[None, Unset, bool]):
        ignore_dots_for_gmail_addresses (Union[None, Unset, bool]):
    """

    allowlist: Union[None, Unset, bool] = UNSET
    blocklist: Union[None, Unset, bool] = UNSET
    block_email_subaddresses: Union[None, Unset, bool] = UNSET
    block_disposable_email_domains: Union[None, Unset, bool] = UNSET
    ignore_dots_for_gmail_addresses: Union[None, Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        allowlist: Union[None, Unset, bool]
        if isinstance(self.allowlist, Unset):
            allowlist = UNSET
        else:
            allowlist = self.allowlist

        blocklist: Union[None, Unset, bool]
        if isinstance(self.blocklist, Unset):
            blocklist = UNSET
        else:
            blocklist = self.blocklist

        block_email_subaddresses: Union[None, Unset, bool]
        if isinstance(self.block_email_subaddresses, Unset):
            block_email_subaddresses = UNSET
        else:
            block_email_subaddresses = self.block_email_subaddresses

        block_disposable_email_domains: Union[None, Unset, bool]
        if isinstance(self.block_disposable_email_domains, Unset):
            block_disposable_email_domains = UNSET
        else:
            block_disposable_email_domains = self.block_disposable_email_domains

        ignore_dots_for_gmail_addresses: Union[None, Unset, bool]
        if isinstance(self.ignore_dots_for_gmail_addresses, Unset):
            ignore_dots_for_gmail_addresses = UNSET
        else:
            ignore_dots_for_gmail_addresses = self.ignore_dots_for_gmail_addresses

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if allowlist is not UNSET:
            field_dict["allowlist"] = allowlist
        if blocklist is not UNSET:
            field_dict["blocklist"] = blocklist
        if block_email_subaddresses is not UNSET:
            field_dict["block_email_subaddresses"] = block_email_subaddresses
        if block_disposable_email_domains is not UNSET:
            field_dict["block_disposable_email_domains"] = block_disposable_email_domains
        if ignore_dots_for_gmail_addresses is not UNSET:
            field_dict["ignore_dots_for_gmail_addresses"] = ignore_dots_for_gmail_addresses

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_allowlist(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        allowlist = _parse_allowlist(d.pop("allowlist", UNSET))

        def _parse_blocklist(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        blocklist = _parse_blocklist(d.pop("blocklist", UNSET))

        def _parse_block_email_subaddresses(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        block_email_subaddresses = _parse_block_email_subaddresses(d.pop("block_email_subaddresses", UNSET))

        def _parse_block_disposable_email_domains(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        block_disposable_email_domains = _parse_block_disposable_email_domains(
            d.pop("block_disposable_email_domains", UNSET)
        )

        def _parse_ignore_dots_for_gmail_addresses(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        ignore_dots_for_gmail_addresses = _parse_ignore_dots_for_gmail_addresses(
            d.pop("ignore_dots_for_gmail_addresses", UNSET)
        )

        update_instance_restrictions_body = cls(
            allowlist=allowlist,
            blocklist=blocklist,
            block_email_subaddresses=block_email_subaddresses,
            block_disposable_email_domains=block_disposable_email_domains,
            ignore_dots_for_gmail_addresses=ignore_dots_for_gmail_addresses,
        )

        return update_instance_restrictions_body
