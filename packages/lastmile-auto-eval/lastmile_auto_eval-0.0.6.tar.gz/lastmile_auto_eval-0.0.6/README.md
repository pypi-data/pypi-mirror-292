A library for using evaluation models (either default ones provided by LastMile or your own that are fine-tuned) to evaluate LLMs.

Evaluations are run on dataframes that include any combination of `input`, `ground_truth`, and `output` columns. At least one of these columns must be defined and all values must be strings.

## Synchronous Requests

You can use `evaluate()` and `stream_evaluate()` for non-streaming and streaming results.

## Asynchronous Requests

You can use `submit_job()` which will return a job_id string. Ideal for evaluations that don't require immediate responses. With a job_id (ex: `cm0c4bxwo002kpe01h5j4zj2y`) you can:

1. Read job info: `<host_url>/api/auto_eval_job/read?id=<job_id>`

   Ex: https://lastmileai.dev/api/auto_eval_job/read?id=cm0c4bxwo002kpe01h5j4zj2y

2. Retrieve results: `<host_url>/api/auto_eval_job/get_results?id=<job_id>`

   Ex: https://lastmileai.dev/api/auto_eval_job/get_results?id=cm0c4bxwo002kpe01h5j4zj2y

## Example Usage

```python

from lastmile_auto_eval import (
    EvaluationMetric,
    EvaluationResult,
    evaluate,
    stream_evaluate,
    submit_job,
)
import pandas as pd
import json
from typing import Any, Generator

queries = ["what color is the sky?", "what color is the sky?"]
correct_answer = "the sky is blue"
incorrect_answer = "the sky is red"
ground_truth_values = [correct_answer, correct_answer]
responses = [correct_answer, incorrect_answer]

df = pd.DataFrame(
    {
        "input": queries,
        "ground_truth": ground_truth_values,
        "output": responses,
    }
)

# Non-streaming
result: EvaluationResult = evaluate(
    dataframe=df,
    metrics=[
        EvaluationMetric.P_FAITHFUL,
        EvaluationMetric.SUMMARIZATION,
    ],
)
print(json.dumps(result, indent=2))

# Response will look something like this:
"""
{
  "p_faithful": [
    0.999255359172821,
    0.00011296303273411468
  ],
  "summarization": [
    0.9995583891868591,
    6.86283819959499e-05
  ]
}
"""

# Response-streaming
result_iterator: Generator[EvaluationResult, Any, Any] = (
    stream_evaluate(
        dataframe=df,
        metrics=[
            EvaluationMetric.P_FAITHFUL,
            EvaluationMetric.SUMMARIZATION,
        ],
    )
)
for result_chunk in result_iterator:
    print(json.dumps(result_chunk, indent=2))

# Bidirectional-streaming
def gen_df_stream(input: list[str], gt: list[str], output: list[str]):
    for i in range(len(input)):
        df_chunk = pd.DataFrame(
            {
                "input": [input[i]],
                "ground_truth": [gt[i]],
                "output": [output[i]],
            }
        )
        yield df_chunk

df_iterator = gen_df_stream(
    input=queries, gt=ground_truth_values, output=responses
)
result_iterator: Generator[EvaluationResult, Any, Any] = (
    stream_evaluate(
        dataframe=df_iterator,
        metrics=[
            EvaluationMetric.P_FAITHFUL,
            EvaluationMetric.SUMMARIZATION,
        ],
    )
)
for result_chunk in result_iterator:
    print(json.dumps(result_chunk, indent=2))

# Async request
job_id = submit_job(
    df,
    metrics=[
        EvaluationMetric.P_FAITHFUL,
        EvaluationMetric.SUMMARIZATION,
    ],
)
print(f"{job_id=}")
```
