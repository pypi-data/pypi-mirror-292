"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from .basesdk import BaseSDK
from mistralai_gcp import models, utils
from mistralai_gcp._hooks import HookContext
from mistralai_gcp.types import Nullable, OptionalNullable, UNSET
from mistralai_gcp.utils import eventstreaming
from typing import Any, AsyncGenerator, Generator, Optional, Union

class Fim(BaseSDK):
    r"""Fill-in-the-middle API."""
    
    
    def stream(
        self, *,
        model: Nullable[str],
        prompt: str,
        temperature: Optional[float] = 0.7,
        top_p: Optional[float] = 1,
        max_tokens: OptionalNullable[int] = UNSET,
        min_tokens: OptionalNullable[int] = UNSET,
        stream: Optional[bool] = True,
        stop: Optional[Union[models.FIMCompletionStreamRequestStop, models.FIMCompletionStreamRequestStopTypedDict]] = None,
        random_seed: OptionalNullable[int] = UNSET,
        suffix: OptionalNullable[str] = UNSET,
        retries: OptionalNullable[utils.RetryConfig] = UNSET,
        server_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ) -> Optional[Generator[models.CompletionEvent, None, None]]:
        r"""Stream fim completion

        Mistral AI provides the ability to stream responses back to a client in order to allow partial results for certain requests. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. Otherwise, the server will hold the request open until the timeout or until completion, with the response containing the full result as JSON.

        :param model: ID of the model to use. Only compatible for now with:   - `codestral-2405`   - `codestral-latest`
        :param prompt: The text/code to complete.
        :param temperature: What sampling temperature to use, between 0.0 and 1.0. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or `top_p` but not both.
        :param top_p: Nucleus sampling, where the model considers the results of the tokens with `top_p` probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or `temperature` but not both.
        :param max_tokens: The maximum number of tokens to generate in the completion. The token count of your prompt plus `max_tokens` cannot exceed the model's context length.
        :param min_tokens: The minimum number of tokens to generate in the completion.
        :param stream: 
        :param stop: Stop generation if this token is detected. Or if one of these tokens is detected when providing an array
        :param random_seed: The seed to use for random sampling. If set, different calls will generate deterministic results.
        :param suffix: Optional text/code that adds more context for the model. When given a `prompt` and a `suffix` the model will fill what is between them. When `suffix` is not provided, the model will simply execute completion starting with `prompt`.
        :param retries: Override the default retry configuration for this method
        :param server_url: Override the default server URL for this method
        :param timeout_ms: Override the default request timeout configuration for this method in milliseconds
        """
        base_url = None
        url_variables = None
        if timeout_ms is None:
            timeout_ms = self.sdk_configuration.timeout_ms
        
        if server_url is not None:
            base_url = server_url
        
        request = models.FIMCompletionStreamRequest(
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            min_tokens=min_tokens,
            stream=stream,
            stop=stop,
            random_seed=random_seed,
            prompt=prompt,
            suffix=suffix,
        )
        
        req = self.build_request(
            method="POST",
            path="/streamRawPredict#fim",
            base_url=base_url,
            url_variables=url_variables,
            request=request,
            request_body_required=True,
            request_has_path_params=False,
            request_has_query_params=True,
            user_agent_header="user-agent",
            accept_header_value="text/event-stream",
            security=self.sdk_configuration.security,
            get_serialized_body=lambda: utils.serialize_request_body(request, False, False, "json", models.FIMCompletionStreamRequest),
            timeout_ms=timeout_ms,
        )
        
        if retries == UNSET:
            if self.sdk_configuration.retry_config is not UNSET:
                retries = self.sdk_configuration.retry_config

        retry_config = None
        if isinstance(retries, utils.RetryConfig):
            retry_config = (retries, [
                "429",
                "500",
                "502",
                "503",
                "504"
            ])                
        
        http_res = self.do_request(
            hook_ctx=HookContext(operation_id="stream_fim", oauth2_scopes=[], security_source=self.sdk_configuration.security),
            request=req,
            error_status_codes=["422","4XX","5XX"],
            stream=True,
            retry_config=retry_config
        )
        
        data: Any = None
        if utils.match_response(http_res, "200", "text/event-stream"):
            return eventstreaming.stream_events(http_res, lambda raw: utils.unmarshal_json(raw, models.CompletionEvent), sentinel="[DONE]")
        if utils.match_response(http_res, "422", "application/json"):
            data = utils.unmarshal_json(http_res.text, models.HTTPValidationErrorData)
            raise models.HTTPValidationError(data=data)
        if utils.match_response(http_res, ["4XX","5XX"], "*"):
            raise models.SDKError("API error occurred", http_res.status_code, http_res.text, http_res)
        
        content_type = http_res.headers.get("Content-Type")
        raise models.SDKError(f"Unexpected response received (code: {http_res.status_code}, type: {content_type})", http_res.status_code, http_res.text, http_res)

    
    
    async def stream_async(
        self, *,
        model: Nullable[str],
        prompt: str,
        temperature: Optional[float] = 0.7,
        top_p: Optional[float] = 1,
        max_tokens: OptionalNullable[int] = UNSET,
        min_tokens: OptionalNullable[int] = UNSET,
        stream: Optional[bool] = True,
        stop: Optional[Union[models.FIMCompletionStreamRequestStop, models.FIMCompletionStreamRequestStopTypedDict]] = None,
        random_seed: OptionalNullable[int] = UNSET,
        suffix: OptionalNullable[str] = UNSET,
        retries: OptionalNullable[utils.RetryConfig] = UNSET,
        server_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ) -> Optional[AsyncGenerator[models.CompletionEvent, None]]:
        r"""Stream fim completion

        Mistral AI provides the ability to stream responses back to a client in order to allow partial results for certain requests. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. Otherwise, the server will hold the request open until the timeout or until completion, with the response containing the full result as JSON.

        :param model: ID of the model to use. Only compatible for now with:   - `codestral-2405`   - `codestral-latest`
        :param prompt: The text/code to complete.
        :param temperature: What sampling temperature to use, between 0.0 and 1.0. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or `top_p` but not both.
        :param top_p: Nucleus sampling, where the model considers the results of the tokens with `top_p` probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or `temperature` but not both.
        :param max_tokens: The maximum number of tokens to generate in the completion. The token count of your prompt plus `max_tokens` cannot exceed the model's context length.
        :param min_tokens: The minimum number of tokens to generate in the completion.
        :param stream: 
        :param stop: Stop generation if this token is detected. Or if one of these tokens is detected when providing an array
        :param random_seed: The seed to use for random sampling. If set, different calls will generate deterministic results.
        :param suffix: Optional text/code that adds more context for the model. When given a `prompt` and a `suffix` the model will fill what is between them. When `suffix` is not provided, the model will simply execute completion starting with `prompt`.
        :param retries: Override the default retry configuration for this method
        :param server_url: Override the default server URL for this method
        :param timeout_ms: Override the default request timeout configuration for this method in milliseconds
        """
        base_url = None
        url_variables = None
        if timeout_ms is None:
            timeout_ms = self.sdk_configuration.timeout_ms
        
        if server_url is not None:
            base_url = server_url
        
        request = models.FIMCompletionStreamRequest(
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            min_tokens=min_tokens,
            stream=stream,
            stop=stop,
            random_seed=random_seed,
            prompt=prompt,
            suffix=suffix,
        )
        
        req = self.build_request(
            method="POST",
            path="/streamRawPredict#fim",
            base_url=base_url,
            url_variables=url_variables,
            request=request,
            request_body_required=True,
            request_has_path_params=False,
            request_has_query_params=True,
            user_agent_header="user-agent",
            accept_header_value="text/event-stream",
            security=self.sdk_configuration.security,
            get_serialized_body=lambda: utils.serialize_request_body(request, False, False, "json", models.FIMCompletionStreamRequest),
            timeout_ms=timeout_ms,
        )
        
        if retries == UNSET:
            if self.sdk_configuration.retry_config is not UNSET:
                retries = self.sdk_configuration.retry_config

        retry_config = None
        if isinstance(retries, utils.RetryConfig):
            retry_config = (retries, [
                "429",
                "500",
                "502",
                "503",
                "504"
            ])                
        
        http_res = await self.do_request_async(
            hook_ctx=HookContext(operation_id="stream_fim", oauth2_scopes=[], security_source=self.sdk_configuration.security),
            request=req,
            error_status_codes=["422","4XX","5XX"],
            stream=True,
            retry_config=retry_config
        )
        
        data: Any = None
        if utils.match_response(http_res, "200", "text/event-stream"):
            return eventstreaming.stream_events_async(http_res, lambda raw: utils.unmarshal_json(raw, models.CompletionEvent), sentinel="[DONE]")
        if utils.match_response(http_res, "422", "application/json"):
            data = utils.unmarshal_json(http_res.text, models.HTTPValidationErrorData)
            raise models.HTTPValidationError(data=data)
        if utils.match_response(http_res, ["4XX","5XX"], "*"):
            raise models.SDKError("API error occurred", http_res.status_code, http_res.text, http_res)
        
        content_type = http_res.headers.get("Content-Type")
        raise models.SDKError(f"Unexpected response received (code: {http_res.status_code}, type: {content_type})", http_res.status_code, http_res.text, http_res)

    
    
    def complete(
        self, *,
        model: Nullable[str],
        prompt: str,
        temperature: Optional[float] = 0.7,
        top_p: Optional[float] = 1,
        max_tokens: OptionalNullable[int] = UNSET,
        min_tokens: OptionalNullable[int] = UNSET,
        stream: Optional[bool] = False,
        stop: Optional[Union[models.FIMCompletionRequestStop, models.FIMCompletionRequestStopTypedDict]] = None,
        random_seed: OptionalNullable[int] = UNSET,
        suffix: OptionalNullable[str] = UNSET,
        retries: OptionalNullable[utils.RetryConfig] = UNSET,
        server_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ) -> Optional[models.FIMCompletionResponse]:
        r"""Fim Completion

        FIM completion.

        :param model: ID of the model to use. Only compatible for now with:   - `codestral-2405`   - `codestral-latest`
        :param prompt: The text/code to complete.
        :param temperature: What sampling temperature to use, between 0.0 and 1.0. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or `top_p` but not both.
        :param top_p: Nucleus sampling, where the model considers the results of the tokens with `top_p` probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or `temperature` but not both.
        :param max_tokens: The maximum number of tokens to generate in the completion. The token count of your prompt plus `max_tokens` cannot exceed the model's context length.
        :param min_tokens: The minimum number of tokens to generate in the completion.
        :param stream: Whether to stream back partial progress. If set, tokens will be sent as data-only server-side events as they become available, with the stream terminated by a data: [DONE] message. Otherwise, the server will hold the request open until the timeout or until completion, with the response containing the full result as JSON.
        :param stop: Stop generation if this token is detected. Or if one of these tokens is detected when providing an array
        :param random_seed: The seed to use for random sampling. If set, different calls will generate deterministic results.
        :param suffix: Optional text/code that adds more context for the model. When given a `prompt` and a `suffix` the model will fill what is between them. When `suffix` is not provided, the model will simply execute completion starting with `prompt`.
        :param retries: Override the default retry configuration for this method
        :param server_url: Override the default server URL for this method
        :param timeout_ms: Override the default request timeout configuration for this method in milliseconds
        """
        base_url = None
        url_variables = None
        if timeout_ms is None:
            timeout_ms = self.sdk_configuration.timeout_ms
        
        if server_url is not None:
            base_url = server_url
        
        request = models.FIMCompletionRequest(
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            min_tokens=min_tokens,
            stream=stream,
            stop=stop,
            random_seed=random_seed,
            prompt=prompt,
            suffix=suffix,
        )
        
        req = self.build_request(
            method="POST",
            path="/rawPredict#fim",
            base_url=base_url,
            url_variables=url_variables,
            request=request,
            request_body_required=True,
            request_has_path_params=False,
            request_has_query_params=True,
            user_agent_header="user-agent",
            accept_header_value="application/json",
            security=self.sdk_configuration.security,
            get_serialized_body=lambda: utils.serialize_request_body(request, False, False, "json", models.FIMCompletionRequest),
            timeout_ms=timeout_ms,
        )
        
        if retries == UNSET:
            if self.sdk_configuration.retry_config is not UNSET:
                retries = self.sdk_configuration.retry_config

        retry_config = None
        if isinstance(retries, utils.RetryConfig):
            retry_config = (retries, [
                "429",
                "500",
                "502",
                "503",
                "504"
            ])                
        
        http_res = self.do_request(
            hook_ctx=HookContext(operation_id="fim_completion_v1_fim_completions_post", oauth2_scopes=[], security_source=self.sdk_configuration.security),
            request=req,
            error_status_codes=["422","4XX","5XX"],
            retry_config=retry_config
        )
        
        data: Any = None
        if utils.match_response(http_res, "200", "application/json"):
            return utils.unmarshal_json(http_res.text, Optional[models.FIMCompletionResponse])
        if utils.match_response(http_res, "422", "application/json"):
            data = utils.unmarshal_json(http_res.text, models.HTTPValidationErrorData)
            raise models.HTTPValidationError(data=data)
        if utils.match_response(http_res, ["4XX","5XX"], "*"):
            raise models.SDKError("API error occurred", http_res.status_code, http_res.text, http_res)
        
        content_type = http_res.headers.get("Content-Type")
        raise models.SDKError(f"Unexpected response received (code: {http_res.status_code}, type: {content_type})", http_res.status_code, http_res.text, http_res)

    
    
    async def complete_async(
        self, *,
        model: Nullable[str],
        prompt: str,
        temperature: Optional[float] = 0.7,
        top_p: Optional[float] = 1,
        max_tokens: OptionalNullable[int] = UNSET,
        min_tokens: OptionalNullable[int] = UNSET,
        stream: Optional[bool] = False,
        stop: Optional[Union[models.FIMCompletionRequestStop, models.FIMCompletionRequestStopTypedDict]] = None,
        random_seed: OptionalNullable[int] = UNSET,
        suffix: OptionalNullable[str] = UNSET,
        retries: OptionalNullable[utils.RetryConfig] = UNSET,
        server_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ) -> Optional[models.FIMCompletionResponse]:
        r"""Fim Completion

        FIM completion.

        :param model: ID of the model to use. Only compatible for now with:   - `codestral-2405`   - `codestral-latest`
        :param prompt: The text/code to complete.
        :param temperature: What sampling temperature to use, between 0.0 and 1.0. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or `top_p` but not both.
        :param top_p: Nucleus sampling, where the model considers the results of the tokens with `top_p` probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or `temperature` but not both.
        :param max_tokens: The maximum number of tokens to generate in the completion. The token count of your prompt plus `max_tokens` cannot exceed the model's context length.
        :param min_tokens: The minimum number of tokens to generate in the completion.
        :param stream: Whether to stream back partial progress. If set, tokens will be sent as data-only server-side events as they become available, with the stream terminated by a data: [DONE] message. Otherwise, the server will hold the request open until the timeout or until completion, with the response containing the full result as JSON.
        :param stop: Stop generation if this token is detected. Or if one of these tokens is detected when providing an array
        :param random_seed: The seed to use for random sampling. If set, different calls will generate deterministic results.
        :param suffix: Optional text/code that adds more context for the model. When given a `prompt` and a `suffix` the model will fill what is between them. When `suffix` is not provided, the model will simply execute completion starting with `prompt`.
        :param retries: Override the default retry configuration for this method
        :param server_url: Override the default server URL for this method
        :param timeout_ms: Override the default request timeout configuration for this method in milliseconds
        """
        base_url = None
        url_variables = None
        if timeout_ms is None:
            timeout_ms = self.sdk_configuration.timeout_ms
        
        if server_url is not None:
            base_url = server_url
        
        request = models.FIMCompletionRequest(
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            min_tokens=min_tokens,
            stream=stream,
            stop=stop,
            random_seed=random_seed,
            prompt=prompt,
            suffix=suffix,
        )
        
        req = self.build_request(
            method="POST",
            path="/rawPredict#fim",
            base_url=base_url,
            url_variables=url_variables,
            request=request,
            request_body_required=True,
            request_has_path_params=False,
            request_has_query_params=True,
            user_agent_header="user-agent",
            accept_header_value="application/json",
            security=self.sdk_configuration.security,
            get_serialized_body=lambda: utils.serialize_request_body(request, False, False, "json", models.FIMCompletionRequest),
            timeout_ms=timeout_ms,
        )
        
        if retries == UNSET:
            if self.sdk_configuration.retry_config is not UNSET:
                retries = self.sdk_configuration.retry_config

        retry_config = None
        if isinstance(retries, utils.RetryConfig):
            retry_config = (retries, [
                "429",
                "500",
                "502",
                "503",
                "504"
            ])                
        
        http_res = await self.do_request_async(
            hook_ctx=HookContext(operation_id="fim_completion_v1_fim_completions_post", oauth2_scopes=[], security_source=self.sdk_configuration.security),
            request=req,
            error_status_codes=["422","4XX","5XX"],
            retry_config=retry_config
        )
        
        data: Any = None
        if utils.match_response(http_res, "200", "application/json"):
            return utils.unmarshal_json(http_res.text, Optional[models.FIMCompletionResponse])
        if utils.match_response(http_res, "422", "application/json"):
            data = utils.unmarshal_json(http_res.text, models.HTTPValidationErrorData)
            raise models.HTTPValidationError(data=data)
        if utils.match_response(http_res, ["4XX","5XX"], "*"):
            raise models.SDKError("API error occurred", http_res.status_code, http_res.text, http_res)
        
        content_type = http_res.headers.get("Content-Type")
        raise models.SDKError(f"Unexpected response received (code: {http_res.status_code}, type: {content_type})", http_res.status_code, http_res.text, http_res)

    
