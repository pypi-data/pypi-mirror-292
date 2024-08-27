from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.verify_session_body import VerifySessionBody
from ...types import Response


def _get_kwargs(
    session_id: str,
    *,
    body: VerifySessionBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/sessions/{session_id}/verify",
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
    if response.status_code == HTTPStatus.GONE:
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
    session_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: VerifySessionBody,
) -> Response[Any]:
    """Verify a session

     Returns the session if it is authenticated, otherwise returns an error.
    WARNING: This endpoint is deprecated and will be removed in future versions. We strongly recommend
    switching to networkless verification using short-lived session tokens,
             which is implemented transparently in all recent SDK versions (e.g. [NodeJS
    SDK](https://clerk.com/docs/backend-requests/handling/nodejs#clerk-express-require-auth)).
             For more details on how networkless verification works, refer to our [Session Tokens
    documentation](https://clerk.com/docs/backend-requests/resources/session-tokens).

    Args:
        session_id (str):
        body (VerifySessionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        session_id=session_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    session_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: VerifySessionBody,
) -> Response[Any]:
    """Verify a session

     Returns the session if it is authenticated, otherwise returns an error.
    WARNING: This endpoint is deprecated and will be removed in future versions. We strongly recommend
    switching to networkless verification using short-lived session tokens,
             which is implemented transparently in all recent SDK versions (e.g. [NodeJS
    SDK](https://clerk.com/docs/backend-requests/handling/nodejs#clerk-express-require-auth)).
             For more details on how networkless verification works, refer to our [Session Tokens
    documentation](https://clerk.com/docs/backend-requests/resources/session-tokens).

    Args:
        session_id (str):
        body (VerifySessionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        session_id=session_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
