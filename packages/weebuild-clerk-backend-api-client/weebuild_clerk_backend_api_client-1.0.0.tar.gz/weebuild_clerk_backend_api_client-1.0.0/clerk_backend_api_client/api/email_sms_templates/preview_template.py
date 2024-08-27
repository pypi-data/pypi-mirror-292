from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.preview_template_body import PreviewTemplateBody
from ...models.preview_template_response_200 import PreviewTemplateResponse200
from ...types import Response


def _get_kwargs(
    template_type: str,
    slug: str,
    *,
    body: PreviewTemplateBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/templates/{template_type}/{slug}/preview",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, PreviewTemplateResponse200]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PreviewTemplateResponse200.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = cast(Any, None)
        return response_404
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = cast(Any, None)
        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, PreviewTemplateResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    template_type: str,
    slug: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PreviewTemplateBody,
) -> Response[Union[Any, PreviewTemplateResponse200]]:
    """Preview changes to a template

     Returns a preview of a template for a given template_type, slug and body

    Args:
        template_type (str):
        slug (str):
        body (PreviewTemplateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PreviewTemplateResponse200]]
    """

    kwargs = _get_kwargs(
        template_type=template_type,
        slug=slug,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    template_type: str,
    slug: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PreviewTemplateBody,
) -> Optional[Union[Any, PreviewTemplateResponse200]]:
    """Preview changes to a template

     Returns a preview of a template for a given template_type, slug and body

    Args:
        template_type (str):
        slug (str):
        body (PreviewTemplateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PreviewTemplateResponse200]
    """

    return sync_detailed(
        template_type=template_type,
        slug=slug,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    template_type: str,
    slug: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PreviewTemplateBody,
) -> Response[Union[Any, PreviewTemplateResponse200]]:
    """Preview changes to a template

     Returns a preview of a template for a given template_type, slug and body

    Args:
        template_type (str):
        slug (str):
        body (PreviewTemplateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PreviewTemplateResponse200]]
    """

    kwargs = _get_kwargs(
        template_type=template_type,
        slug=slug,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    template_type: str,
    slug: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PreviewTemplateBody,
) -> Optional[Union[Any, PreviewTemplateResponse200]]:
    """Preview changes to a template

     Returns a preview of a template for a given template_type, slug and body

    Args:
        template_type (str):
        slug (str):
        body (PreviewTemplateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PreviewTemplateResponse200]
    """

    return (
        await asyncio_detailed(
            template_type=template_type,
            slug=slug,
            client=client,
            body=body,
        )
    ).parsed
