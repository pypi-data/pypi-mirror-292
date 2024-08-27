from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.toggle_template_delivery_body import ToggleTemplateDeliveryBody
from ...models.toggle_template_delivery_template_type import ToggleTemplateDeliveryTemplateType
from ...types import Response


def _get_kwargs(
    template_type: ToggleTemplateDeliveryTemplateType,
    slug: str,
    *,
    body: ToggleTemplateDeliveryBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/templates/{template_type}/{slug}/toggle_delivery",
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
    template_type: ToggleTemplateDeliveryTemplateType,
    slug: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ToggleTemplateDeliveryBody,
) -> Response[Any]:
    """Toggle the delivery by Clerk for a template of a given type and slug

     Toggles the delivery by Clerk for a template of a given type and slug.
    If disabled, Clerk will not deliver the resulting email or SMS.
    The app developer will need to listen to the `email.created` or `sms.created` webhooks in order to
    handle delivery themselves.

    Args:
        template_type (ToggleTemplateDeliveryTemplateType):
        slug (str):
        body (ToggleTemplateDeliveryBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
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


async def asyncio_detailed(
    template_type: ToggleTemplateDeliveryTemplateType,
    slug: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ToggleTemplateDeliveryBody,
) -> Response[Any]:
    """Toggle the delivery by Clerk for a template of a given type and slug

     Toggles the delivery by Clerk for a template of a given type and slug.
    If disabled, Clerk will not deliver the resulting email or SMS.
    The app developer will need to listen to the `email.created` or `sms.created` webhooks in order to
    handle delivery themselves.

    Args:
        template_type (ToggleTemplateDeliveryTemplateType):
        slug (str):
        body (ToggleTemplateDeliveryBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        template_type=template_type,
        slug=slug,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
