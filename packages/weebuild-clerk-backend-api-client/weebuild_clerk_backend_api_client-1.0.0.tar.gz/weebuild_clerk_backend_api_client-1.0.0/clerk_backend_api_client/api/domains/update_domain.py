from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.update_domain_body import UpdateDomainBody
from ...types import Response


def _get_kwargs(
    domain_id: str,
    *,
    body: UpdateDomainBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "patch",
        "url": f"/domains/{domain_id}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if response.status_code == HTTPStatus.OK:
        return None
    if response.status_code == HTTPStatus.BAD_REQUEST:
        return None
    if response.status_code == HTTPStatus.NOT_FOUND:
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
    domain_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateDomainBody,
) -> Response[Any]:
    """Update a domain

     The `proxy_url` can be updated only for production instances.
    Update one of the instance's domains. Both primary and satellite domains can be updated.
    If you choose to use Clerk via proxy, use this endpoint to specify the `proxy_url`.
    Whenever you decide you'd rather switch to DNS setup for Clerk, simply set `proxy_url`
    to `null` for the domain. When you update a production instance's primary domain name,
    you have to make sure that you've completed all the necessary setup steps for DNS and
    emails to work. Expect downtime otherwise. Updating a primary domain's name will also
    update the instance's home origin, affecting the default application paths.

    Args:
        domain_id (str):
        body (UpdateDomainBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    domain_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateDomainBody,
) -> Response[Any]:
    """Update a domain

     The `proxy_url` can be updated only for production instances.
    Update one of the instance's domains. Both primary and satellite domains can be updated.
    If you choose to use Clerk via proxy, use this endpoint to specify the `proxy_url`.
    Whenever you decide you'd rather switch to DNS setup for Clerk, simply set `proxy_url`
    to `null` for the domain. When you update a production instance's primary domain name,
    you have to make sure that you've completed all the necessary setup steps for DNS and
    emails to work. Expect downtime otherwise. Updating a primary domain's name will also
    update the instance's home origin, affecting the default application paths.

    Args:
        domain_id (str):
        body (UpdateDomainBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        domain_id=domain_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
