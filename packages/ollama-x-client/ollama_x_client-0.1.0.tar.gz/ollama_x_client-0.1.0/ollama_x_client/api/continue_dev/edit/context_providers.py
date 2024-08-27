from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ollama_x_client import errors
from ollama_x_client.client import AuthenticatedClient, Client
from ollama_x_client.models.api_error_access_denied import APIErrorAccessDenied
from ollama_x_client.models.code_context_provider import CodeContextProvider
from ollama_x_client.models.codebase_context_provider import CodebaseContextProvider
from ollama_x_client.models.diff_context_provider import DiffContextProvider
from ollama_x_client.models.docs_context_provider import DocsContextProvider
from ollama_x_client.models.http_validation_error import HTTPValidationError
from ollama_x_client.models.open_context_provider import OpenContextProvider
from ollama_x_client.models.search_context_provider import SearchContextProvider
from ollama_x_client.models.url_context_provider import UrlContextProvider
from ollama_x_client.types import Response


def _get_kwargs(
    project_id: str,
    *,
    body: Union[
        List[
            Union[
                "CodeContextProvider",
                "CodebaseContextProvider",
                "DiffContextProvider",
                "DocsContextProvider",
                "OpenContextProvider",
                "SearchContextProvider",
                "UrlContextProvider",
            ]
        ],
        None,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "patch",
        "url": f"/continue.dev/project/{project_id}/context-providers",
    }

    _body: Union[List[Dict[str, Any]], None]
    if isinstance(body, list):
        _body = []
        for body_type_0_item_data in body:
            body_type_0_item: Dict[str, Any]
            if isinstance(body_type_0_item_data, CodeContextProvider):
                body_type_0_item = body_type_0_item_data.to_dict()
            elif isinstance(body_type_0_item_data, CodebaseContextProvider):
                body_type_0_item = body_type_0_item_data.to_dict()
            elif isinstance(body_type_0_item_data, DiffContextProvider):
                body_type_0_item = body_type_0_item_data.to_dict()
            elif isinstance(body_type_0_item_data, DocsContextProvider):
                body_type_0_item = body_type_0_item_data.to_dict()
            elif isinstance(body_type_0_item_data, OpenContextProvider):
                body_type_0_item = body_type_0_item_data.to_dict()
            elif isinstance(body_type_0_item_data, SearchContextProvider):
                body_type_0_item = body_type_0_item_data.to_dict()
            else:
                body_type_0_item = body_type_0_item_data.to_dict()

            _body.append(body_type_0_item)

    else:
        _body = body

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
    project_id: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        List[
            Union[
                "CodeContextProvider",
                "CodebaseContextProvider",
                "DiffContextProvider",
                "DocsContextProvider",
                "OpenContextProvider",
                "SearchContextProvider",
                "UrlContextProvider",
            ]
        ],
        None,
    ],
) -> Response[Union[APIErrorAccessDenied, HTTPValidationError]]:
    """Edit Context Providers

     Edit project context providers.

    Args:
        project_id (str):
        body (Union[List[Union['CodeContextProvider', 'CodebaseContextProvider',
            'DiffContextProvider', 'DocsContextProvider', 'OpenContextProvider',
            'SearchContextProvider', 'UrlContextProvider']], None]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[APIErrorAccessDenied, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        List[
            Union[
                "CodeContextProvider",
                "CodebaseContextProvider",
                "DiffContextProvider",
                "DocsContextProvider",
                "OpenContextProvider",
                "SearchContextProvider",
                "UrlContextProvider",
            ]
        ],
        None,
    ],
) -> Optional[Union[APIErrorAccessDenied, HTTPValidationError]]:
    """Edit Context Providers

     Edit project context providers.

    Args:
        project_id (str):
        body (Union[List[Union['CodeContextProvider', 'CodebaseContextProvider',
            'DiffContextProvider', 'DocsContextProvider', 'OpenContextProvider',
            'SearchContextProvider', 'UrlContextProvider']], None]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[APIErrorAccessDenied, HTTPValidationError]
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        List[
            Union[
                "CodeContextProvider",
                "CodebaseContextProvider",
                "DiffContextProvider",
                "DocsContextProvider",
                "OpenContextProvider",
                "SearchContextProvider",
                "UrlContextProvider",
            ]
        ],
        None,
    ],
) -> Response[Union[APIErrorAccessDenied, HTTPValidationError]]:
    """Edit Context Providers

     Edit project context providers.

    Args:
        project_id (str):
        body (Union[List[Union['CodeContextProvider', 'CodebaseContextProvider',
            'DiffContextProvider', 'DocsContextProvider', 'OpenContextProvider',
            'SearchContextProvider', 'UrlContextProvider']], None]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[APIErrorAccessDenied, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        List[
            Union[
                "CodeContextProvider",
                "CodebaseContextProvider",
                "DiffContextProvider",
                "DocsContextProvider",
                "OpenContextProvider",
                "SearchContextProvider",
                "UrlContextProvider",
            ]
        ],
        None,
    ],
) -> Optional[Union[APIErrorAccessDenied, HTTPValidationError]]:
    """Edit Context Providers

     Edit project context providers.

    Args:
        project_id (str):
        body (Union[List[Union['CodeContextProvider', 'CodebaseContextProvider',
            'DiffContextProvider', 'DocsContextProvider', 'OpenContextProvider',
            'SearchContextProvider', 'UrlContextProvider']], None]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[APIErrorAccessDenied, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
            body=body,
        )
    ).parsed
