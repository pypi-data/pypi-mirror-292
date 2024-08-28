"""
Client-facing API for interacting with the evaluation service.
"""

from typing import Any, Generator, Optional

import pandas as pd

from lastmile_auto_eval import eval_api_pb2
from lastmile_auto_eval.api_utils import (
    EvaluationMetric,
    EvaluationResult,
    ModelSpecifier,
    StreamConfig,
    build_grpc_stub,
    build_request_body,
    build_request_body_iterator,
    build_stream_config,
    load_api_token,
    load_host_url,
    parse_response,
)


def evaluate(
    dataframe: pd.DataFrame | Generator[pd.DataFrame, Any, Any],
    metrics: list[EvaluationMetric | str | ModelSpecifier] = [
        EvaluationMetric.P_FAITHFUL
    ],
    lastmile_api_token: Optional[str] = None,
    host_url: Optional[str] = None,
) -> EvaluationResult:
    """
    Evaluate a dataframe for a set of metrics.

    params:
        dataframe: pd.DataFrame | Generator[pd.DataFrame, Any, Any]
            The dataframe to evaluate. Can
            contain columns for "input", "ground_truth", "output". It
            must contain at least one of these columns. The values within
            each column must be strings.
        metrics: list[EvaluationMetric | str | ModelSpecifier]
            A list of metrics you wish to evaluate. You can use a provided
            EvaluationMetric or supply a string identifier of a model
            that you have trained yourself. You can also provide a
            ModelSpecifier to provide more fine-grained control over which
            models to evaluate such as defining a specific version id.
            If not provided, will default to [EvaluationMetric.P_FAITHFUL].
        lastmile_api_token: The API token for the LastMile API. If not provided,
            will try to get the token from the LASTMILE_API_TOKEN
            environment variable.
            You can create a token from the "API Tokens" section from this website:
            https://lastmileai.dev/settings?page=tokens
        host_url: The host URL for hosting the evaluation service, which you can use
            to point to your own deployed service. If not provided, will try
            to get it from the LASTMILE_EVAL_HOST_URL environment variable. If
            it's still not provided, will default to "https://eval.lastmileai.dev"
            where it is hosted and provided by LastMile.

    Returns:
        EvaluationResult:
            A dictionary containing the scores for each metric. EvaluationResult is
            of type dict[str, list[float]]

    Example:
    ```
    df = pd.DataFrame(
        {
            "input": ['input1', 'input2'],
            "ground_truth": ['gt1', 'gt2'],
            "output": ['output1', 'output2'],
        }
    )
    result = evaluate(
        dataframe=df,
        metrics=[EvaluationMetric.P_FAITHFUL, EvaluationMetric.SUMMARIZATION],
    )
    # result looks like:
    # { # First index corresponds to ('input1', 'gt1', 'output1')
    #     'p_faithful': [0.9936350584030151, 0.00011290529073448852],
    #     'summarization': [0.9955607652664185, 6.859706627437845e-05],
    # }
    ```
    """
    api_token = lastmile_api_token or load_api_token()

    stream_config = build_stream_config(dataframe, stream_output=False)
    if stream_config != StreamConfig.NO_STREAMING:
        raise NotImplementedError(
            f"Unsupported configuration {stream_config} on method `evaluate`. To stream responses, please use `stream_evaluate` method instead."
        )

    request_body = build_request_body(dataframe, metrics)
    stub = build_grpc_stub(host_url or load_host_url())

    metadata = [("authorization", f"Bearer {api_token}")]
    response: eval_api_pb2.Response = stub.GetEvaluationData(  # type: ignore
        request_body,
        metadata=metadata,
    )
    return parse_response(response)


# TODO (rossdan): Maybe change name of this method to `gen_evaluate()` instead?
# See comments: https://app.graphite.dev/github/pr/lastmile-ai/lmai/291/Eval-Server-23-n-Refactor-server-s-internal-evaluate-helper-method-to-handle-streaming-and-non-streaming-separately#comment-PRRC_kwDOMFVIEc5liLgK
def stream_evaluate(
    dataframe: pd.DataFrame | Generator[pd.DataFrame, Any, Any],
    metrics: list[EvaluationMetric | str | ModelSpecifier] = [
        EvaluationMetric.P_FAITHFUL
    ],
    lastmile_api_token: Optional[str] = None,
    host_url: Optional[str] = None,
) -> Generator[EvaluationResult, Any, Any]:
    """
    Evaluate a dataframe for a set of metrics. Same as `evaluate()` but returns a generator
    to stream the outputs.

    params:
        See `evaluate()`

    Returns:
        Generator[EvaluationResult, Any, Any]:
            A dictionary containing the scores for each metric. EvaluationResult is
            of type dict[str, list[float]]

    Example:
    ```
    df = pd.DataFrame(
        {
            "input": ['input1', 'input2'],
            "ground_truth": ['gt1', 'gt2'],
            "output": ['output1', 'output2'],
        }
    )
    result_iterator = evaluate(
        dataframe=df,
        metrics=[EvaluationMetric.P_FAITHFUL, EvaluationMetric.SUMMARIZATION],
    )
    for i, result in enumerate(result_iterator):
        # result looks like:
        # { # ith index corresponds to (input[i], ground_truth[i], output[i])
        #     'p_faithful': [0.9936350584030151],
        #     'summarization': [0.9955607652664185],
        # }
        pass
    ```
    """
    api_token = lastmile_api_token or load_api_token()

    stream_config = build_stream_config(dataframe, stream_output=True)

    stub = build_grpc_stub(host_url or load_host_url())

    metadata = [("authorization", f"Bearer {api_token}")]
    match stream_config:
        case StreamConfig.RESPONSE_STREAMING_ONLY:
            request_body = build_request_body(dataframe, metrics)
            response_iterator: Generator[eval_api_pb2.Response, Any, Any] = stub.StreamEvaluationData(  # type: ignore
                request_body,
                metadata=metadata,
            )
            for response_chunk in response_iterator:
                yield parse_response(response_chunk)
        case StreamConfig.BIDIRECTIONAL_STREAMING:
            request_body_iterator = build_request_body_iterator(
                dataframe, metrics
            )
            response_iterator: Generator[eval_api_pb2.Response, Any, Any] = stub.ExchangeEvaluationData(  # type: ignore
                request_body_iterator,
                metadata=metadata,
            )
            for response_chunk in response_iterator:
                yield parse_response(response_chunk)
        case _:
            # Should never get here but keep for safety
            raise NotImplementedError(
                f"Unsupported configuration {stream_config} on method `stream_evaluate`. For non-streaming responses, please use `evaluate` method instead."
            )


def submit_job(
    dataframe: pd.DataFrame,
    metrics: list[EvaluationMetric | str | ModelSpecifier] = [
        EvaluationMetric.P_FAITHFUL
    ],
    lastmile_api_token: Optional[str] = None,
    host_url: Optional[str] = None,
) -> str:
    """
    Submit an asynchronous request to evaluate a dataframe for a set of models.

    Same as `evaluate()` but performs evaluation offline with larger rate limits. 
    Ideal for evaluations that don't require immediate responses. Returns a job_id 
    string for interacting with the evaluation job and results.

    1. Read job info: `<host_url>/api/auto_eval_job/read?id=<job_id>`

        Ex: https://lastmileai.dev/api/auto_eval_job/read?id=cm0c4bxwo002kpe01h5j4zj2y
    2. Retrieve results: `<host_url>/api/auto_eval_job/get_results?id=<job_id>`

        Ex: https://lastmileai.dev/api/auto_eval_job/get_results?id=cm0c4bxwo002kpe01h5j4zj2y

    Returns:
        str (job_id):
            A job_id that can be used to check the status of the job and retrieve results

    Example:
    ```
    df = pd.DataFrame(
        {
            "input": ['input1', 'input2'],
            "ground_truth": ['gt1', 'gt2'],
            "output": ['output1', 'output2'],
        }
    )
    job_id = submit_job(
        dataframe=df,
        metrics=[EvaluationMetric.P_FAITHFUL, EvaluationMetric.SUMMARIZATION],
    )
    # job_id looks something like this: `cm0c4bxwo002kpe01h5j4zj2y`

    # # Read job info: https://lastmileai.dev/api/auto_eval_job/read?id=<job_id>
    # {
    #     "id": "cm0c4bxwo002kpe01h5j4zj2y",
    #     "createdAt": "2024-08-21T20:06:07.625Z",
    #     "updatedAt": "2024-08-21T20:06:13.311Z",
    #     "creatorId": "clz1fugol0000w97en9lrbmxz",
    #     "status": "COMPLETED",
    #     "visibility": "PRIVATE"
    # }

    # # Retrieve results: https://lastmileai.dev/api/auto_eval_job/get_results?id=<job_id>
    # [
    #     {
    #         "data": {
    #             "input": "input1",
    #             "output": "output1",
    #             "ground_truth": "gt1"
    #         },
    #         "requestIndex": 0,
    #         "scores": [
    #             {
    #                 "metric": "p_faithful",
    #                 "score": 0.000900355284102261,
    #             },
    #             {
    #                 "metric": "summarization",
    #                 "score": 0.659818291664124,
    #             }
    #         ]
    #     },
    #     {
    #         "data": {
    #             "input": "input2",
    #             "output": "output2",
    #             "ground_truth": "gt2"
    #         },
    #         "requestIndex": 1,
    #         "scores": [
    #             {
    #                 "metric": "p_faithful",
    #                 "score": 0.000532948120962828,
    #             },
    #             {
    #                 "metric": "summarization",
    #                 "score": 0.957729160785675,
    #             }
    #         ]
    #     }
    # ]
    ```
    """
    api_token = lastmile_api_token or load_api_token()
    stream_config = build_stream_config(dataframe, stream_output=False)

    stub = build_grpc_stub(host_url or load_host_url())

    metadata = [("authorization", f"Bearer {api_token}")]
    match stream_config:
        case StreamConfig.NO_STREAMING:
            assert isinstance(dataframe, pd.DataFrame)
            request_body = build_request_body(dataframe, metrics)
            job: eval_api_pb2.Job = stub.SubmitEvaluation(  # type: ignore
                request_body,
                metadata=metadata,
            )
            return job.id
        case StreamConfig.REQUEST_STREAMING_ONLY:
            raise NotImplementedError(
                f"Unsupported configuration {stream_config} on method `submit_job`. Streaming inputs for asynchronous requests is currently not supported so please pass in a dataframe object instead of a dataframe generator."
            )
        case _:
            # Should never get here but keep for safety
            raise NotImplementedError(
                f"That's weird! Unsupported configuration {stream_config} on method `submit_job`. For some reason we believe output should be a stream object even though we should be returning jobId. Please file a bug to https://discord.com/invite/xBhNKTetGx and we'll do our best to resolve it right away!"
            )
