from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.update_user_body import UpdateUserBody
from ...types import Response


def _get_kwargs(
    user_id: str,
    *,
    body: UpdateUserBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "patch",
        "url": f"/users/{user_id}",
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
    if response.status_code == HTTPStatus.UNAUTHORIZED:
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
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateUserBody,
) -> Response[Any]:
    r"""Update a user

     Update a user's attributes.

    You can set the user's primary contact identifiers (email address and phone numbers) by updating the
    `primary_email_address_id` and `primary_phone_number_id` attributes respectively.
    Both IDs should correspond to verified identifications that belong to the user.

    You can remove a user's username by setting the username attribute to null or the blank string \"\".
    This is a destructive action; the identification will be deleted forever.
    Usernames can be removed only if they are optional in your instance settings and there's at least
    one other identifier which can be used for authentication.

    This endpoint allows changing a user's password. When passing the `password` parameter directly you
    have two further options.
    You can ignore the password policy checks for your instance by setting the `skip_password_checks`
    parameter to `true`.
    You can also choose to sign the user out of all their active sessions on any device once the
    password is updated. Just set `sign_out_of_other_sessions` to `true`.

    Args:
        user_id (str):
        body (UpdateUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateUserBody,
) -> Response[Any]:
    r"""Update a user

     Update a user's attributes.

    You can set the user's primary contact identifiers (email address and phone numbers) by updating the
    `primary_email_address_id` and `primary_phone_number_id` attributes respectively.
    Both IDs should correspond to verified identifications that belong to the user.

    You can remove a user's username by setting the username attribute to null or the blank string \"\".
    This is a destructive action; the identification will be deleted forever.
    Usernames can be removed only if they are optional in your instance settings and there's at least
    one other identifier which can be used for authentication.

    This endpoint allows changing a user's password. When passing the `password` parameter directly you
    have two further options.
    You can ignore the password policy checks for your instance by setting the `skip_password_checks`
    parameter to `true`.
    You can also choose to sign the user out of all their active sessions on any device once the
    password is updated. Just set `sign_out_of_other_sessions` to `true`.

    Args:
        user_id (str):
        body (UpdateUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
