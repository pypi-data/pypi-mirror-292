from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    limit: Union[Unset, float] = 10.0,
    offset: Union[Unset, float] = 0.0,
    order_by: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params["order_by"] = order_by

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/organizations/{organization_id}/memberships",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if response.status_code == HTTPStatus.OK:
        return None
    if response.status_code == HTTPStatus.UNAUTHORIZED:
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
    organization_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    limit: Union[Unset, float] = 10.0,
    offset: Union[Unset, float] = 0.0,
    order_by: Union[Unset, str] = UNSET,
) -> Response[Any]:
    """Get a list of all members of an organization

     Retrieves all user memberships for the given organization

    Args:
        organization_id (str):
        limit (Union[Unset, float]):  Default: 10.0.
        offset (Union[Unset, float]):  Default: 0.0.
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        limit=limit,
        offset=offset,
        order_by=order_by,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    organization_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    limit: Union[Unset, float] = 10.0,
    offset: Union[Unset, float] = 0.0,
    order_by: Union[Unset, str] = UNSET,
) -> Response[Any]:
    """Get a list of all members of an organization

     Retrieves all user memberships for the given organization

    Args:
        organization_id (str):
        limit (Union[Unset, float]):  Default: 10.0.
        offset (Union[Unset, float]):  Default: 0.0.
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        limit=limit,
        offset=offset,
        order_by=order_by,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
