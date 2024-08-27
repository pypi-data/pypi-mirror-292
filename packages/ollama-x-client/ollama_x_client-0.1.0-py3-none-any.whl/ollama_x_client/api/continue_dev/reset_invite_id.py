from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ollama_x_client import errors
from ollama_x_client.client import AuthenticatedClient, Client
from ollama_x_client.models.api_error_access_denied import APIErrorAccessDenied
from ollama_x_client.models.http_validation_error import HTTPValidationError
from ollama_x_client.types import UNSET, Response


def _get_kwargs(
    *,
    project_id: str,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["project_id"] = project_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/continue.dev/reset-invite-id",
        "params": params,
    }

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
    client: Union[AuthenticatedClient, Client],
    project_id: str,
) -> Response[Union[APIErrorAccessDenied, HTTPValidationError]]:
    """Get project config.

     Resets invite id in project.

    Args:
        project_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[APIErrorAccessDenied, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    project_id: str,
) -> Optional[Union[APIErrorAccessDenied, HTTPValidationError]]:
    """Get project config.

     Resets invite id in project.

    Args:
        project_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[APIErrorAccessDenied, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        project_id=project_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    project_id: str,
) -> Response[Union[APIErrorAccessDenied, HTTPValidationError]]:
    """Get project config.

     Resets invite id in project.

    Args:
        project_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[APIErrorAccessDenied, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    project_id: str,
) -> Optional[Union[APIErrorAccessDenied, HTTPValidationError]]:
    """Get project config.

     Resets invite id in project.

    Args:
        project_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[APIErrorAccessDenied, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            project_id=project_id,
        )
    ).parsed
