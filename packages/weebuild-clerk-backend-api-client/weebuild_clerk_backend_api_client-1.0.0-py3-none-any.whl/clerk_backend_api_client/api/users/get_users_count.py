from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    email_address: Union[Unset, List[str]] = UNSET,
    phone_number: Union[Unset, List[str]] = UNSET,
    external_id: Union[Unset, List[str]] = UNSET,
    username: Union[Unset, List[str]] = UNSET,
    web3_wallet: Union[Unset, List[str]] = UNSET,
    user_id: Union[Unset, List[str]] = UNSET,
    query: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_email_address: Union[Unset, List[str]] = UNSET
    if not isinstance(email_address, Unset):
        json_email_address = email_address

    params["email_address"] = json_email_address

    json_phone_number: Union[Unset, List[str]] = UNSET
    if not isinstance(phone_number, Unset):
        json_phone_number = phone_number

    params["phone_number"] = json_phone_number

    json_external_id: Union[Unset, List[str]] = UNSET
    if not isinstance(external_id, Unset):
        json_external_id = external_id

    params["external_id"] = json_external_id

    json_username: Union[Unset, List[str]] = UNSET
    if not isinstance(username, Unset):
        json_username = username

    params["username"] = json_username

    json_web3_wallet: Union[Unset, List[str]] = UNSET
    if not isinstance(web3_wallet, Unset):
        json_web3_wallet = web3_wallet

    params["web3_wallet"] = json_web3_wallet

    json_user_id: Union[Unset, List[str]] = UNSET
    if not isinstance(user_id, Unset):
        json_user_id = user_id

    params["user_id"] = json_user_id

    params["query"] = query

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/users/count",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if response.status_code == HTTPStatus.OK:
        return None
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    email_address: Union[Unset, List[str]] = UNSET,
    phone_number: Union[Unset, List[str]] = UNSET,
    external_id: Union[Unset, List[str]] = UNSET,
    username: Union[Unset, List[str]] = UNSET,
    web3_wallet: Union[Unset, List[str]] = UNSET,
    user_id: Union[Unset, List[str]] = UNSET,
    query: Union[Unset, str] = UNSET,
) -> Response[Any]:
    """Count users

     Returns a total count of all users that match the given filtering criteria.

    Args:
        email_address (Union[Unset, List[str]]):
        phone_number (Union[Unset, List[str]]):
        external_id (Union[Unset, List[str]]):
        username (Union[Unset, List[str]]):
        web3_wallet (Union[Unset, List[str]]):
        user_id (Union[Unset, List[str]]):
        query (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        email_address=email_address,
        phone_number=phone_number,
        external_id=external_id,
        username=username,
        web3_wallet=web3_wallet,
        user_id=user_id,
        query=query,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    email_address: Union[Unset, List[str]] = UNSET,
    phone_number: Union[Unset, List[str]] = UNSET,
    external_id: Union[Unset, List[str]] = UNSET,
    username: Union[Unset, List[str]] = UNSET,
    web3_wallet: Union[Unset, List[str]] = UNSET,
    user_id: Union[Unset, List[str]] = UNSET,
    query: Union[Unset, str] = UNSET,
) -> Response[Any]:
    """Count users

     Returns a total count of all users that match the given filtering criteria.

    Args:
        email_address (Union[Unset, List[str]]):
        phone_number (Union[Unset, List[str]]):
        external_id (Union[Unset, List[str]]):
        username (Union[Unset, List[str]]):
        web3_wallet (Union[Unset, List[str]]):
        user_id (Union[Unset, List[str]]):
        query (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        email_address=email_address,
        phone_number=phone_number,
        external_id=external_id,
        username=username,
        web3_wallet=web3_wallet,
        user_id=user_id,
        query=query,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
