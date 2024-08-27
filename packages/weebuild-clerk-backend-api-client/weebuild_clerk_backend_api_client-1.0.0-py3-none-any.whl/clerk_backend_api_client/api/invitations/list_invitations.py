from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.list_invitations_status import ListInvitationsStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Union[Unset, float] = 10.0,
    offset: Union[Unset, float] = 0.0,
    status: Union[Unset, ListInvitationsStatus] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/invitations",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if response.status_code == HTTPStatus.OK:
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
    limit: Union[Unset, float] = 10.0,
    offset: Union[Unset, float] = 0.0,
    status: Union[Unset, ListInvitationsStatus] = UNSET,
) -> Response[Any]:
    """List all invitations

     Returns all non-revoked invitations for your application, sorted by creation date

    Args:
        limit (Union[Unset, float]):  Default: 10.0.
        offset (Union[Unset, float]):  Default: 0.0.
        status (Union[Unset, ListInvitationsStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    limit: Union[Unset, float] = 10.0,
    offset: Union[Unset, float] = 0.0,
    status: Union[Unset, ListInvitationsStatus] = UNSET,
) -> Response[Any]:
    """List all invitations

     Returns all non-revoked invitations for your application, sorted by creation date

    Args:
        limit (Union[Unset, float]):  Default: 10.0.
        offset (Union[Unset, float]):  Default: 0.0.
        status (Union[Unset, ListInvitationsStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
