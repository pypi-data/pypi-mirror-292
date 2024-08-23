import os
import uuid
from dataclasses import dataclass
from typing import Dict, List

from wrapt import wrap_function_wrapper

from zenetics.client import APIClient

try:
    import openai
except ImportError:
    raise ImportError(
        "Please install the OpenAI Python package using `pip install openai`"
    )


@dataclass
class Result:
    content: str
    content_type: str

    def to_dict(self):
        return {
            "content": self.content,
            "contentType": self.content_type,
        }


@dataclass
class Message:
    role: str
    content: str
    version: str

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "version": self.version,
        }


@dataclass
class Prompt:
    version: str
    messages: List[Message]

    def to_dict(self):
        return {
            "version": self.version,
            "messages": [message.to_dict() for message in self.messages],
        }


@dataclass
class Data:
    score: float
    content: str

    def to_dict(self):
        return {
            "score": self.score,
            "content": self.content,
        }


@dataclass
class InputContext:
    label: str
    data: List[Dict]

    def to_dict(self):
        return {"label": self.label, "data": [datum.to_dict() for datum in self.data]}


@dataclass
class Completion:
    id: str
    type: str
    model_params: Dict
    usage: Dict
    prompt: Prompt
    result: Result
    input_context: List[InputContext]

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "modelParams": self.model_params,
            "usage": self.usage,
            "prompt": self.prompt.to_dict(),
            "result": self.result.to_dict(),
            "inputContext": [context.to_dict() for context in self.input_context],
        }


@dataclass
class Session:
    id: str
    organization_id: str
    application_id: str
    completions: List[Completion]

    def to_dict(self):
        return {
            "id": self.id,
            "completions": [completion.to_dict() for completion in self.completions],
        }


class Zenetics:
    def __init__(self, api_key: str, app_id: str, api_client: APIClient):
        self.api_key = api_key
        self.app_id = app_id
        self.api_client = api_client

    def capture(self, request, result):

        session_result = None
        input_context = None

        if len(result.choices) > 0:
            session_result = Result(
                content=result.choices[0].message.content,
                content_type="text",
            )

        opts_input_context = request.get("opts", {}).get("inputContext")

        if opts_input_context:
            input_context = [
                InputContext(
                    label=context["label"],
                    data=[
                        Data(score=datum["score"], content=datum["content"])
                        for datum in context["data"]
                    ],
                )
                for context in opts_input_context
            ]

        completion = Completion(
            id=str(uuid.uuid4()),
            type="text",
            model_params={},
            usage={
                "completion_tokens": result.usage.completion_tokens,
                "prompt_tokens": result.usage.prompt_tokens,
                "total_tokens": result.usage.total_tokens,
            },
            prompt=Prompt(
                version="1.0",
                messages=[
                    Message(
                        role=message["role"],
                        content=message["content"],
                        version="1.0",
                    )
                    for message in request["messages"]
                ],
            ),
            result=session_result,
            input_context=input_context,
        )

        session = Session(
            id=str(uuid.uuid4()),
            completions=[completion],
            organization_id="default",
            application_id="default",
        )

        self.api_client.post(session.to_dict(), self.api_key, self.app_id)


api_key = os.environ.get("ZENETICS_API_KEY")
app_id = os.environ.get("ZENETICS_APP_ID")
host = os.environ.get("ZENETICS_HOST")

if not api_key:
    raise ValueError("ZENETICS_API_KEY environment variable is required")

if not app_id:
    raise ValueError("ZENETICS_APP_ID environment variable is required")

if not host:
    host = "https://api.zenetics.io"

api_client = APIClient(host)

zenetics = Zenetics(api_key, app_id, api_client)


def extract_args(kwargs):
    opts = kwargs.copy()

    zenetics_opts = opts.pop("zenetics_opts", {})

    request = {
        "messages": opts.get("messages"),
        "opts": zenetics_opts,
    }

    return request, opts


def trace_function(wrapped, instance, args, kwargs):
    request, forward_kwargs = extract_args(kwargs)
    result = wrapped(*args, **forward_kwargs)
    zenetics.capture(request, result)
    return result


wrap_function_wrapper(
    "openai.resources.chat.completions",
    "Completions.create",
    trace_function,
)
