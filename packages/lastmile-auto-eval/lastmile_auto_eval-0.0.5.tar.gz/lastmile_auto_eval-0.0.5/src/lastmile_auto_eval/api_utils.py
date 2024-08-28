"""
Utils file for defining types, constants, etc
"""

import os
from enum import Enum
from typing import Any, Generator, NewType, Optional
from dataclasses import dataclass
from dotenv import find_dotenv, load_dotenv
from textwrap import dedent

import grpc
import pandas as pd
from lastmile_auto_eval import eval_api_pb2, eval_api_pb2_grpc

EvaluationResult = NewType("EvaluationResult", dict[str, list[float]])


class EvaluationMetric(str, Enum):
    P_FAITHFUL = "p_faithful"
    RELEVANCE = "relevance"
    TOXICITY = "toxicity"
    QA = "qa"
    SUMMARIZATION = "summarization"


@dataclass(frozen=True)
class ModelSpecifier:
    """
    Use this to specify more fine-grained control over which models to evaluate.
    """

    identifier: EvaluationMetric | str
    version: str = "latest"


DEFAULT_METRICS = [EvaluationMetric.P_FAITHFUL]
DEFAULT_EVAL_HOST_URL = "https://eval.lastmileai.dev"


class StreamConfig(str, Enum):
    """
    Internal intermediate flag to make it easier to know
    which streaming-type request we should make.
    """

    NO_STREAMING = "no_streaming"
    REQUEST_STREAMING_ONLY = "request_streaming_only"
    RESPONSE_STREAMING_ONLY = "response_streaming_only"
    BIDIRECTIONAL_STREAMING = "bidirectional_streaming"


def build_request_body(
    dataframe: pd.DataFrame,
    metrics: list[EvaluationMetric | str | ModelSpecifier],
) -> eval_api_pb2.RequestBody:  # pylint: disable=no-member
    input = _get_col_as_list(dataframe, "input")
    ground_truth = _get_col_as_list(dataframe, "ground_truth")
    output = _get_col_as_list(dataframe, "output")

    request_body = eval_api_pb2.RequestBody()  # pylint: disable=no-member
    if input is not None:
        request_body.input.values.extend(input)
    if ground_truth is not None:
        request_body.ground_truth.values.extend(ground_truth)
    if output is not None:
        request_body.output.values.extend(output)

    model_specifiers: list[
        eval_api_pb2.ModelSpecifier  # pylint: disable=no-member
    ] = list(
        map(
            lambda m: (
                eval_api_pb2.ModelSpecifier(  # pylint: disable=no-member
                    identifier=m.identifier, version=m.version
                )
                if isinstance(m, ModelSpecifier)
                else eval_api_pb2.ModelSpecifier(  # pylint: disable=no-member
                    identifier=m
                )
            ),
            metrics,
        )
    )
    request_body.model_specifiers.extend(model_specifiers)
    return request_body


def build_request_body_iterator(
    dataframe: Generator[pd.DataFrame, Any, Any],
    metrics: list[EvaluationMetric | str | ModelSpecifier],
) -> Generator[eval_api_pb2.RequestBody, Any, Any]:
    for df_chunk in dataframe:
        yield build_request_body(df_chunk, metrics)


def parse_response(
    response: eval_api_pb2.Response,
) -> EvaluationResult:  # pylint: disable=no-member
    model_scores = {k: list(v.values) for k, v in response.scores.items()}
    return model_scores


def _get_col_as_list(
    dataframe: pd.DataFrame, col_name: str
) -> Optional[list[str]]:
    if col_name in dataframe.columns:
        col_as_list: list[Any] = dataframe[col_name].tolist()
        for item in col_as_list:
            if not isinstance(item, str):
                raise ValueError(
                    f"Column '{col_name}' contains non-string value {item}. Please ensure all values are strings."
                )
        return col_as_list
    return None


def build_grpc_stub(
    host_url: str,
) -> eval_api_pb2_grpc.EvalApiStub:  # pylint: disable=no-member
    """
    Helper function to create a gRPC stub for the evaluation server
    """
    endpoint_url = _sanitize_endpoint_url(host_url)
    credentials = grpc.ssl_channel_credentials()  # type: ignore
    channel = grpc.secure_channel(endpoint_url, credentials)  # type: ignore
    return eval_api_pb2_grpc.EvalApiStub(channel)


def build_stream_config(
    input_df: pd.DataFrame | Generator[pd.DataFrame, Any, Any],
    stream_output: bool,
) -> StreamConfig:
    """
    Helper function to create a StreamConfig object instead of having to manually
    check the input dataframe and stream params every time
    """
    stream_input = isinstance(input_df, Generator)
    match stream_input, stream_output:
        case False, False:
            return StreamConfig.NO_STREAMING
        case True, False:
            return StreamConfig.REQUEST_STREAMING_ONLY
        case True, True:
            return StreamConfig.BIDIRECTIONAL_STREAMING
        case _:
            return StreamConfig.RESPONSE_STREAMING_ONLY


# TODO: Maybe should create helper library just for loading in tokens
# since we re-use this logic in all our packages and repos
def load_api_token():
    """
    Load the Lastmile API token from the environment.
    """
    _load_dotenv_from_cwd()

    token_key = "LASTMILE_API_TOKEN"
    token = os.getenv(token_key)
    if token is None:
        raise ValueError(
            dedent(
                f"""Missing API token: {token_key}.
            * If you don't have a LastMile token:
                please log in here https://lastmileai.dev/settings?page=tokens
                then click "Create new token" next to "API Tokens".
            * Once you have your token:
                please create a .env file in your current directory, 
                and add the following entry:
                {token_key}=<your token>

            """
            )
        )

    return token


def load_host_url() -> str:
    """
    Load the host url for the running the eval service from the environment.
    If not provided, will default to "https://eval.lastmileai.dev"
    """
    _load_dotenv_from_cwd()
    url_key = "LASTMILE_EVAL_HOST_URL"
    host_url = os.getenv(url_key)
    return host_url or DEFAULT_EVAL_HOST_URL


def _load_dotenv_from_cwd() -> bool:
    """
    Helper method needed to ensure that when we load the .env file, we load it
    from user's current cwd, not the published package location, which could
    otherwise lead to error since we will be unable to detect an .env file.
    """
    dotenv_path = find_dotenv(usecwd=True)
    return load_dotenv(dotenv_path=dotenv_path)


def _sanitize_endpoint_url(url: str) -> str:
    """
    Need to remove http:// or https:// or www. prefix from URL since
    we are using the gRPC protocol
    """
    return (
        url.removeprefix("http://")
        .removeprefix("https://")
        .removeprefix("www.")
    )
