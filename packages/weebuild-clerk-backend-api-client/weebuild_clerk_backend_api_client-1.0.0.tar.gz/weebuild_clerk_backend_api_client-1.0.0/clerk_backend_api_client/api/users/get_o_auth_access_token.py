from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_o_auth_access_token_response_200_item import GetOAuthAccessTokenResponse200Item
from ...types import Response


def _get_kwargs(
    user_id: str,
    provider: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/users/{user_id}/oauth_access_tokens/{provider}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, List["GetOAuthAccessTokenResponse200Item"]]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetOAuthAccessTokenResponse200Item.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = cast(Any, None)
        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, List["GetOAuthAccessTokenResponse200Item"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    provider: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, List["GetOAuthAccessTokenResponse200Item"]]]:
    """Retrieve the OAuth access token of a user

     Fetch the corresponding OAuth access token for a user that has previously authenticated with a
    particular OAuth provider.
    For OAuth 2.0, if the access token has expired and we have a corresponding refresh token, the access
    token will be refreshed transparently the new one will be returned.

    Args:
        user_id (str):
        provider (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, List['GetOAuthAccessTokenResponse200Item']]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        provider=provider,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    provider: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, List["GetOAuthAccessTokenResponse200Item"]]]:
    """Retrieve the OAuth access token of a user

     Fetch the corresponding OAuth access token for a user that has previously authenticated with a
    particular OAuth provider.
    For OAuth 2.0, if the access token has expired and we have a corresponding refresh token, the access
    token will be refreshed transparently the new one will be returned.

    Args:
        user_id (str):
        provider (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, List['GetOAuthAccessTokenResponse200Item']]
    """

    return sync_detailed(
        user_id=user_id,
        provider=provider,
        client=client,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    provider: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, List["GetOAuthAccessTokenResponse200Item"]]]:
    """Retrieve the OAuth access token of a user

     Fetch the corresponding OAuth access token for a user that has previously authenticated with a
    particular OAuth provider.
    For OAuth 2.0, if the access token has expired and we have a corresponding refresh token, the access
    token will be refreshed transparently the new one will be returned.

    Args:
        user_id (str):
        provider (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, List['GetOAuthAccessTokenResponse200Item']]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        provider=provider,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    provider: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, List["GetOAuthAccessTokenResponse200Item"]]]:
    """Retrieve the OAuth access token of a user

     Fetch the corresponding OAuth access token for a user that has previously authenticated with a
    particular OAuth provider.
    For OAuth 2.0, if the access token has expired and we have a corresponding refresh token, the access
    token will be refreshed transparently the new one will be returned.

    Args:
        user_id (str):
        provider (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, List['GetOAuthAccessTokenResponse200Item']]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            provider=provider,
            client=client,
        )
    ).parsed
