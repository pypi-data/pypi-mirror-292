from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_organization_body import CreateOrganizationBody
from ...types import Response


def _get_kwargs(
    *,
    body: CreateOrganizationBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/organizations",
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
    body: CreateOrganizationBody,
) -> Response[Any]:
    r"""Create an organization

     Creates a new organization with the given name for an instance.
    In order to successfully create an organization you need to provide the ID of the User who will
    become the organization administrator.
    You can specify an optional slug for the new organization.
    If provided, the organization slug can contain only lowercase alphanumeric characters (letters and
    digits) and the dash \"-\".
    Organization slugs must be unique for the instance.
    You can provide additional metadata for the organization and set any custom attribute you want.
    Organizations support private and public metadata.
    Private metadata can only be accessed from the Backend API.
    Public metadata can be accessed from the Backend API, and are read-only from the Frontend API.
    The `created_by` user will see this as their [active organization]
    (https://clerk.com/docs/organizations/overview#active-organization)
    the next time they create a session, presuming they don't explicitly set a different organization as
    active before then.

    Args:
        body (CreateOrganizationBody):

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
    body: CreateOrganizationBody,
) -> Response[Any]:
    r"""Create an organization

     Creates a new organization with the given name for an instance.
    In order to successfully create an organization you need to provide the ID of the User who will
    become the organization administrator.
    You can specify an optional slug for the new organization.
    If provided, the organization slug can contain only lowercase alphanumeric characters (letters and
    digits) and the dash \"-\".
    Organization slugs must be unique for the instance.
    You can provide additional metadata for the organization and set any custom attribute you want.
    Organizations support private and public metadata.
    Private metadata can only be accessed from the Backend API.
    Public metadata can be accessed from the Backend API, and are read-only from the Frontend API.
    The `created_by` user will see this as their [active organization]
    (https://clerk.com/docs/organizations/overview#active-organization)
    the next time they create a session, presuming they don't explicitly set a different organization as
    active before then.

    Args:
        body (CreateOrganizationBody):

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
