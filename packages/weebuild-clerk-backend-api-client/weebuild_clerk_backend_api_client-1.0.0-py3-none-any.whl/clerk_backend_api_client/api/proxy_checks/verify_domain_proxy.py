from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.verify_domain_proxy_body import VerifyDomainProxyBody
from ...types import Response


def _get_kwargs(
    *,
    body: VerifyDomainProxyBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/proxy_checks",
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
    body: VerifyDomainProxyBody,
) -> Response[Any]:
    """Verify the proxy configuration for your domain

     This endpoint can be used to validate that a proxy-enabled domain is operational.
    It tries to verify that the proxy URL provided in the parameters maps to a functional proxy that can
    reach the Clerk Frontend API.

    You can use this endpoint before you set a proxy URL for a domain. This way you can ensure that
    switching to proxy-based
    configuration will not lead to downtime for your instance.

    The `proxy_url` parameter allows for testing proxy configurations for domains that don't have a
    proxy URL yet, or operate on
    a different proxy URL than the one provided. It can also be used to re-validate a domain that is
    already configured to work with a proxy.

    Args:
        body (VerifyDomainProxyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: VerifyDomainProxyBody,
) -> Response[Any]:
    """Verify the proxy configuration for your domain

     This endpoint can be used to validate that a proxy-enabled domain is operational.
    It tries to verify that the proxy URL provided in the parameters maps to a functional proxy that can
    reach the Clerk Frontend API.

    You can use this endpoint before you set a proxy URL for a domain. This way you can ensure that
    switching to proxy-based
    configuration will not lead to downtime for your instance.

    The `proxy_url` parameter allows for testing proxy configurations for domains that don't have a
    proxy URL yet, or operate on
    a different proxy URL than the one provided. It can also be used to re-validate a domain that is
    already configured to work with a proxy.

    Args:
        body (VerifyDomainProxyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
