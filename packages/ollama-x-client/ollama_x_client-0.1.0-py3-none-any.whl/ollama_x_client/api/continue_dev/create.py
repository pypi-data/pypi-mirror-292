from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ollama_x_client import errors
from ollama_x_client.client import AuthenticatedClient, Client
from ollama_x_client.models.api_error_access_denied import APIErrorAccessDenied
from ollama_x_client.models.create_project_request import CreateProjectRequest
from ollama_x_client.models.http_validation_error import HTTPValidationError
from ollama_x_client.types import Response


def _get_kwargs(
    *,
    body: CreateProjectRequest,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/continue.dev/",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[APIErrorAccessDenied, HTTPValidationError]]:
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = APIErrorAccessDenied.from_dict(response.json())

        return response_403
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[APIErrorAccessDenied, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: CreateProjectRequest,
) -> Response[Union[APIErrorAccessDenied, HTTPValidationError]]:
    """Create new continue.dev project.

     Create new continue.dev project.

    Args:
        body (CreateProjectRequest): Request to create a new project.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[APIErrorAccessDenied, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: CreateProjectRequest,
) -> Optional[Union[APIErrorAccessDenied, HTTPValidationError]]:
    """Create new continue.dev project.

     Create new continue.dev project.

    Args:
        body (CreateProjectRequest): Request to create a new project.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[APIErrorAccessDenied, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: CreateProjectRequest,
) -> Response[Union[APIErrorAccessDenied, HTTPValidationError]]:
    """Create new continue.dev project.

     Create new continue.dev project.

    Args:
        body (CreateProjectRequest): Request to create a new project.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[APIErrorAccessDenied, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: CreateProjectRequest,
) -> Optional[Union[APIErrorAccessDenied, HTTPValidationError]]:
    """Create new continue.dev project.

     Create new continue.dev project.

    Args:
        body (CreateProjectRequest): Request to create a new project.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[APIErrorAccessDenied, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
