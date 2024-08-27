from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.revoke_organization_invitation_body import RevokeOrganizationInvitationBody
from ...types import Response


def _get_kwargs(
    organization_id: str,
    invitation_id: str,
    *,
    body: RevokeOrganizationInvitationBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/organizations/{organization_id}/invitations/{invitation_id}/revoke",
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
    if response.status_code == HTTPStatus.FORBIDDEN:
        return None
    if response.status_code == HTTPStatus.NOT_FOUND:
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
    invitation_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RevokeOrganizationInvitationBody,
) -> Response[Any]:
    r"""Revoke a pending organization invitation

     Use this request to revoke a previously issued organization invitation.
    Revoking an organization invitation makes it invalid; the invited user will no longer be able to
    join the organization with the revoked invitation.
    Only organization invitations with \"pending\" status can be revoked.
    The request needs the `requesting_user_id` parameter to specify the user which revokes the
    invitation.
    Only users with \"admin\" role can revoke invitations.

    Args:
        organization_id (str):
        invitation_id (str):
        body (RevokeOrganizationInvitationBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        invitation_id=invitation_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    organization_id: str,
    invitation_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RevokeOrganizationInvitationBody,
) -> Response[Any]:
    r"""Revoke a pending organization invitation

     Use this request to revoke a previously issued organization invitation.
    Revoking an organization invitation makes it invalid; the invited user will no longer be able to
    join the organization with the revoked invitation.
    Only organization invitations with \"pending\" status can be revoked.
    The request needs the `requesting_user_id` parameter to specify the user which revokes the
    invitation.
    Only users with \"admin\" role can revoke invitations.

    Args:
        organization_id (str):
        invitation_id (str):
        body (RevokeOrganizationInvitationBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        invitation_id=invitation_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
