from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.upload_organization_logo_body import UploadOrganizationLogoBody
from ...types import Response


def _get_kwargs(
    organization_id: str,
    *,
    body: UploadOrganizationLogoBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": f"/organizations/{organization_id}/logo",
    }

    _body = body.to_multipart()

    _kwargs["files"] = _body

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
    if response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE:
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
    body: UploadOrganizationLogoBody,
) -> Response[Any]:
    """Upload a logo for the organization

     Set or replace an organization's logo, by uploading an image file.
    This endpoint uses the `multipart/form-data` request content type and accepts a file of image type.
    The file size cannot exceed 10MB.
    Only the following file content types are supported: `image/jpeg`, `image/png`, `image/gif`,
    `image/webp`, `image/x-icon`, `image/vnd.microsoft.icon`.

    Args:
        organization_id (str):
        body (UploadOrganizationLogoBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    organization_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadOrganizationLogoBody,
) -> Response[Any]:
    """Upload a logo for the organization

     Set or replace an organization's logo, by uploading an image file.
    This endpoint uses the `multipart/form-data` request content type and accepts a file of image type.
    The file size cannot exceed 10MB.
    Only the following file content types are supported: `image/jpeg`, `image/png`, `image/gif`,
    `image/webp`, `image/x-icon`, `image/vnd.microsoft.icon`.

    Args:
        organization_id (str):
        body (UploadOrganizationLogoBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
