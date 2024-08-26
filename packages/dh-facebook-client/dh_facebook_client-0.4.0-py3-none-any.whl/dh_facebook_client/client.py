from __future__ import annotations

import json
import logging
import urllib.parse
from contextlib import contextmanager
from copy import copy
from types import TracebackType
from typing import Any, Final, Generator, Optional, Type

import backoff
from requests import Response, Session
from requests.exceptions import JSONDecodeError

from .constants import GRAPH_API_URL, GRAPH_API_VERSIONS
from .dataclasses import (
    AppUsageDetails,
    BaseGraphAPIResponse,
    BusinessUseCaseUsageDetails,
    FutureGraphAPIResponse,
    GraphAPIResponse,
    MarketingAPIThrottleInsights,
)
from .error_code import GraphAPICommonErrorCode
from .exceptions import (
    GraphAPIApplicationError,
    GraphAPIBatchRequestLimitReached,
    GraphAPIBatchRequestTimeoutError,
    GraphAPIError,
    GraphAPIServiceError,
    GraphAPITokenError,
    GraphAPIUsageError,
    InvalidAccessToken,
    InvalidGraphAPIVersion,
)
from .typings import (
    ErrorCodeExceptionMap,
    GraphAPIErrorClassType,
    GraphAPIQueryResult,
    JSONTypeSimple,
)

logger = logging.getLogger(__name__)

BATCH_API_REQUESTS_LIMIT: Final = 50


class GraphAPIClient:
    """
    A small client built to interact with the Facebook social graph:
    https://developers.facebook.com/docs/graph-api/overview

    This is currently built minimally for distribution in Dash Hudson
    services where JSON-based requests need to be handled.

    The following functionality is currently unsupported when
    comparing to the official facebook-sdk:
        - HMAC authentication
        - batch request handling
        - file uploading
        - generating oauth redirect urls

    For now API access is provisioned through access tokens,
    if you are unfamiliar with how this works see the following:
    https://developers.facebook.com/docs/facebook-login
    """

    DEFAULT_CODE_EXCEPTION_MAP: Final[ErrorCodeExceptionMap] = {
        (GraphAPICommonErrorCode.API_UNKNOWN.value, None): GraphAPIServiceError,
        (GraphAPICommonErrorCode.API_METHOD.value, None): GraphAPIServiceError,
        (GraphAPICommonErrorCode.API_PERMISSION_DENIED.value, None): GraphAPIApplicationError,
        (GraphAPICommonErrorCode.APPLICATION_BLOCKED_TEMP.value, None): GraphAPIApplicationError,
        (GraphAPICommonErrorCode.API_SESSION.value, None): GraphAPITokenError,
        (GraphAPICommonErrorCode.ACCESS_TOKEN_EXPIRED.value, None): GraphAPITokenError,
        (GraphAPICommonErrorCode.APPLICATION_LIMIT_REACHED.value, None): GraphAPIUsageError,
        (GraphAPICommonErrorCode.API_TOO_MANY_CALLS.value, None): GraphAPIUsageError,
        (GraphAPICommonErrorCode.PAGE_RATE_LIMIT_REACHED.value, None): GraphAPIUsageError,
        (GraphAPICommonErrorCode.CUSTOM_RATE_LIMIT_REACHED.value, None): GraphAPIUsageError,
    }

    def __init__(
        self,
        access_token: str,
        version: str,
        global_timeout: Optional[int] = None,
        params_to_mask: Optional[list[str]] = None,
        retry_params: Optional[dict] = None,
        disable_logger: Optional[bool] = False,
        code_exception_map: Optional[ErrorCodeExceptionMap] = None,
        loose_match_errors: Optional[bool] = False,
    ) -> None:
        """
        Initialize the API client
        :param access_token: An access token provisioned through Facebook login
        :param version: The Graph API version to use (ex: 12.0)
        :param global_timeout: A global request timeout to set
        :param params_to_mask: A list of query parameter names to mask when formatting
            exception messages
        :param disable_logger Disables exception logging if truthy
        :param retry_config Params for https://github.com/litl/backoff#backoffon_exception
        :param code_exception_map: A an error code -> exception map / configuration
        """
        if not access_token or not isinstance(access_token, str):
            raise InvalidAccessToken
        version = (
            version[1:] if isinstance(version, str) and version.lower().startswith('v') else version
        )
        if version not in GRAPH_API_VERSIONS:
            raise InvalidGraphAPIVersion(version)

        self.version = f'v{version}'
        self.global_timeout = global_timeout
        self.params_to_mask = params_to_mask
        self.disable_logger = disable_logger
        # Defaulting to max_tries=0 disables retrying by default
        self.retry_params = retry_params or {'exception': tuple(), 'max_tries': 0}

        self.code_exception_map = self.DEFAULT_CODE_EXCEPTION_MAP
        if code_exception_map:
            self.code_exception_map = {
                **self.DEFAULT_CODE_EXCEPTION_MAP,
                **code_exception_map,
            }

        self._access_token = access_token
        self._session = Session()
        self._session.params = {'access_token': self._access_token}

        self._loose_match_errors = loose_match_errors

        self._batch_mode: bool = False
        self._batch_requests: list[
            tuple[str, str, dict[str, Any] | None, dict[str, Any] | None, FutureGraphAPIResponse]
        ] = []

    def get(
        self,
        path: str,
        params: Optional[dict] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        **kwargs: Any,
    ) -> GraphAPIResponse | FutureGraphAPIResponse:
        """
        :param path: A path pointing to an edge or node
            (ex: /<page_id>/conversations)
        Performs a GET request to the Graph API
        :param params: Query parameters to be included with the request
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An instance of GraphAPIResponse
        """
        return self._do_request(
            method='GET',
            path=path,
            params=params,
            timeout=timeout,
            retry_params=retry_params,
            **kwargs,
        )

    def get_all_pages(
        self,
        path: str,
        params: Optional[dict] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        **kwargs: Any,
    ) -> Generator[GraphAPIResponse, None, None]:
        """
        :param path: A path pointing to an edge or node
            (ex: /<page_id>/conversations)
        Performs a GET request to the Graph API
        :param params: Query parameters to be included with the request
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An iterator containing paginated instances of GraphAPIResponse
        """
        params = copy(params) if params else {}
        params['after'] = None
        while True:
            res = self._do_request(
                method='GET',
                path=path,
                params=params,
                timeout=timeout,
                retry_params=retry_params,
                **kwargs,
            )
            if isinstance(res, FutureGraphAPIResponse):
                raise ValueError('Batch requests are not supported for get_all_pages')
            yield res
            if not res.after_cursor or not res.next_page_url:
                break
            params['after'] = res.after_cursor

    def get_all_pages_from_next_url(
        self,
        next_url: str,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        **kwargs: Any,
    ) -> Generator[GraphAPIResponse, None, None]:
        _next_url = next_url
        while True:
            res = self._do_request(
                method='GET',
                full_url=_next_url,
                timeout=timeout,
                retry_params=retry_params,
                **kwargs,
            )
            if isinstance(res, FutureGraphAPIResponse):
                raise ValueError('Batch requests are not supported for get_all_pages_from_next_url')
            yield res
            if not res.next_page_url:
                break
            _next_url = res.next_page_url

    def post(
        self,
        path: str,
        data: Any,
        params: Optional[Any] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        **kwargs: Any,
    ) -> GraphAPIResponse | FutureGraphAPIResponse:
        """
        Performs a POST request to the Graph API
        :param path: A path pointing to an edge or node
            (ex: /<page_id>/conversations | /<page_id>)
        :param data: The request body to be included
        :param params: Query parameters to be included with the request
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An instance of GraphAPIResponse
        """
        return self._do_request(
            method='POST',
            path=path,
            params=params,
            data=data,
            timeout=timeout,
            retry_params=retry_params,
            **kwargs,
        )

    def delete(
        self,
        path: str,
        params: Optional[dict] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        **kwargs: Any,
    ) -> GraphAPIResponse | FutureGraphAPIResponse:
        """
        Performs a DELETE request to the Graph API
        :param path: A path pointing to a node
            (ex: /<video_id>)
        :param params: Query parameters to be included with the request
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An instance of GraphAPIResponse
        """
        return self._do_request(
            method='DELETE',
            path=path,
            params=params,
            timeout=timeout,
            retry_params=retry_params,
            **kwargs,
        )

    def _do_request(
        self,
        method: str,
        path: str = '',
        full_url: str = '',
        params: Optional[Any] = None,
        data: Optional[Any] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        batch_request: bool = False,
        **kwargs: Any,
    ) -> GraphAPIResponse | FutureGraphAPIResponse:
        """
        Handle Graph API requests. Raise if error body detected and lets ambiguous network
        errors propagate.
        :param method: The HTTP request method
        :param path: A path pointing to an edge or node (ex: /<page_id>/conversations)
        :param params: Query parameters to be included with the request
        :param data: The request body to be included
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An instance of GraphAPIResponse
        """

        if not batch_request and self._batch_mode:
            return self._register_batch_request(
                method, path, full_url, params, data, timeout, retry_params, **kwargs
            )

        @backoff.on_exception(backoff.expo, **(retry_params or self.retry_params))
        def _retry_parameterizer() -> GraphAPIResponse:
            if not path and not full_url:
                raise ValueError('either path or full_url must be specified')

            response = self._session.request(
                method=method,
                url=f'{GRAPH_API_URL}/{self.version}/{path}' if path else full_url,
                params=params,
                data=data,
                timeout=timeout or self.global_timeout,
            )
            result, paging = self._parse_response_body_or_raise(
                response, batch_request=batch_request
            )
            return GraphAPIResponse(
                app_usage_details=AppUsageDetails.from_header(response),
                business_use_case_usage_details=BusinessUseCaseUsageDetails.from_header(response),
                marketing_api_throttle_insights=MarketingAPIThrottleInsights.from_header(response),
                raw_data=result,
                paging=paging,
            )

        return _retry_parameterizer()

    def _register_batch_request(
        self,
        method: str,
        path: str = '',
        full_url: str = '',
        params: Optional[Any] = None,
        data: Optional[Any] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        **kwargs: Any,
    ) -> FutureGraphAPIResponse:
        if full_url:
            raise ValueError('Batch requests are not supported for full_url requests')
        if timeout is not None:
            raise ValueError('Batch requests do not support custom timeouts')
        if retry_params is not None:
            raise ValueError('Batch requests do not support retry_params')
        if kwargs:
            raise ValueError('Batch requests do not support additional kwargs')
        if len(self._batch_requests) >= BATCH_API_REQUESTS_LIMIT:
            raise GraphAPIBatchRequestLimitReached
        future_response = FutureGraphAPIResponse()
        self._batch_requests.append((method, path, params, data, future_response))
        return future_response

    def _parse_response_body_or_raise(
        self, response: Response, *, batch_request: bool = False
    ) -> tuple[
        GraphAPIQueryResult | list[BaseGraphAPIResponse | GraphAPIError], Optional[JSONTypeSimple]
    ]:
        """
        Parse Graph API response body and raise if error details present
        :param response: A response from the Graph API
        :return: Parsed request body and optional paging params
        """
        try:
            response_body = response.json()
        except JSONDecodeError:
            logger.exception(f'Failed to parse response body: {response.text}')
            raise GraphAPIError(response, {'message': 'Failed to parse response body'})

        if batch_request and isinstance(response_body, list):
            return self._parse_batch_response_body(response, response_body)

        if error_details := response_body.get('error'):
            exc = self._get_exc(error_details, response)
            if not self.disable_logger:
                logger.error(str(exc))
            raise exc

        return self._get_results_and_paging(response_body)

    def _get_results_and_paging(
        self, response_body: dict
    ) -> tuple[JSONTypeSimple, None] | tuple[list[JSONTypeSimple], JSONTypeSimple]:
        # If 'data' is present, it means the result is a list of graph nodes and may have
        # paging params as well
        if 'data' in response_body:
            return response_body['data'], response_body.get('paging')
        # If not, the response body is a single graph node without paging params
        return response_body, None

    def _parse_batch_response_body(
        self, response: Response, response_body: list[dict | None]
    ) -> tuple[list[BaseGraphAPIResponse | GraphAPIError], None]:
        results: list[BaseGraphAPIResponse | GraphAPIError] = []
        for item in response_body:
            if item is None:
                results.append(
                    GraphAPIBatchRequestTimeoutError(response, {'message': 'Batch request timeout'})
                )
                continue

            try:
                parsed_body = json.loads(item['body'])
            except JSONDecodeError:
                logger.exception(f'Failed to parse batch response body: {item["body"]}')
                error_details: dict = {'message': 'Failed to parse batch response body', **item}
                results.append(GraphAPIError(response, error_details))
                continue

            if error_details := parsed_body.get('error'):
                results.append(self._get_exc(error_details, response))
            else:
                result, paging = self._get_results_and_paging(parsed_body)
                results.append(BaseGraphAPIResponse(raw_data=result, paging=paging))

        return results, None

    def _get_exc(self, error_details: dict[str, Any], response: Response) -> GraphAPIError:
        # Raise a specific exception if a code mapping is set, custom exceptions take priority
        exc_type = self._get_exc_type(error_details)
        # Log & raise default GraphAPIError if no mapping was found
        return exc_type(
            response=response, error_details=error_details, params_to_mask=self.params_to_mask
        )

    def _get_exc_type(self, error_details: dict[str, Any]) -> GraphAPIErrorClassType:
        code_key: tuple[Any, Any] = (error_details.get('code'), error_details.get('error_subcode'))
        # Raise a specific exception if a code mapping is set, custom exceptions take priority
        if exc_type := self.code_exception_map.get(code_key):
            return exc_type
        # If no mapping was found, try to match loosely
        if self._loose_match_errors and code_key[1]:
            exc_type = self.code_exception_map.get((code_key[0], None))
        return exc_type or GraphAPIError

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self._session.close()

    def reset_batch(self) -> None:
        """
        Resets the batch requests
        """

        self._batch_requests = []

    @contextmanager
    def batch(self) -> Generator[None, None, None]:
        try:
            self._batch_mode = True
            yield
        finally:
            self._batch_mode = False

    def execute_batch(
        self,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        **kwargs: Any,
    ) -> GraphAPIResponse | None:
        """
        Executes a batch request using registered requests

        docs: https://developers.facebook.com/docs/graph-api/batch-requests/
        """
        if not self._batch_requests:
            raise ValueError('execute_batch called without any batch requests')

        batch = []
        future_responses: list[FutureGraphAPIResponse] = []
        for method, path, params, data, future_response in self._batch_requests:
            params_string = urllib.parse.urlencode(params) if params else ''
            relative_url = f'{path}?{params_string}' if params_string else path
            data_string = (
                urllib.parse.urlencode(data) if data and method in ('POST', 'PUT') else None
            )
            batch.append({'method': method, 'relative_url': relative_url, 'body': data_string})
            future_responses.append(future_response)

        self.reset_batch()

        resp = self._do_request(
            method='POST',
            path='.',
            params={'include_headers': 'false'},
            data={'batch': json.dumps(batch)},
            timeout=timeout,
            retry_params=retry_params,
            batch_request=True,
            **kwargs,
        )

        if isinstance(resp, FutureGraphAPIResponse):
            raise ValueError('FutureGraphAPIResponse should not be returned')

        if not isinstance(resp.data, list):
            return resp

        for response_data, future_response in zip(resp.data, future_responses):
            if isinstance(response_data, BaseGraphAPIResponse):
                future_response.set_result(response_data.data)
            elif isinstance(response_data, GraphAPIError):
                future_response.set_exception(response_data)

        return resp
