# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from llama_models.schema_utils import json_schema_type

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated

from llama_toolchain.common.deployment_types import *  # noqa: F403
from llama_toolchain.inference.api import *  # noqa: F403
from llama_toolchain.safety.api.datatypes import *  # noqa: F403
from llama_toolchain.memory.api.datatypes import *  # noqa: F403


@json_schema_type
class AgenticSystemToolDefinition(ToolDefinition):
    execution_config: Optional[RestAPIExecutionConfig] = None
    input_shields: Optional[List[ShieldDefinition]] = Field(default_factory=list)
    output_shields: Optional[List[ShieldDefinition]] = Field(default_factory=list)


class StepCommon(BaseModel):
    turn_id: str
    step_id: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class StepType(Enum):
    inference = "inference"
    tool_execution = "tool_execution"
    shield_call = "shield_call"
    memory_retrieval = "memory_retrieval"


@json_schema_type
class InferenceStep(StepCommon):
    model_config = ConfigDict(protected_namespaces=())

    step_type: Literal[StepType.inference.value] = StepType.inference.value
    model_response: CompletionMessage


@json_schema_type
class ToolExecutionStep(StepCommon):
    step_type: Literal[StepType.tool_execution.value] = StepType.tool_execution.value
    tool_calls: List[ToolCall]
    tool_responses: List[ToolResponse]


@json_schema_type
class ShieldCallStep(StepCommon):
    step_type: Literal[StepType.shield_call.value] = StepType.shield_call.value
    response: ShieldResponse


@json_schema_type
class MemoryRetrievalStep(StepCommon):
    step_type: Literal[StepType.memory_retrieval.value] = (
        StepType.memory_retrieval.value
    )
    memory_bank_ids: List[str]
    documents: List[MemoryBankDocument]
    scores: List[float]


Step = Annotated[
    Union[
        InferenceStep,
        ToolExecutionStep,
        ShieldCallStep,
        MemoryRetrievalStep,
    ],
    Field(discriminator="step_type"),
]


@json_schema_type
class Turn(BaseModel):
    """A single turn in an interaction with an Agentic System."""

    turn_id: str
    session_id: str
    input_messages: List[
        Union[
            UserMessage,
            ToolResponseMessage,
        ]
    ]
    steps: List[Step]
    output_message: CompletionMessage
    started_at: datetime
    completed_at: Optional[datetime] = None


@json_schema_type
class Session(BaseModel):
    """A single session of an interaction with an Agentic System."""

    session_id: str
    session_name: str
    turns: List[Turn]
    started_at: datetime


@json_schema_type
class ToolPromptFormat(Enum):
    """This Enum refers to the prompt format for calling zero shot tools

    `json` --
        Refers to the json format for calling tools.
        The json format takes the form like
        {
            "type": "function",
            "function" : {
                "name": "function_name",
                "description": "function_description",
                "parameters": {...}
            }
        }

    `function_tag` --
        This is an example of how you could define
        your own user defined format for making tool calls.
        The function_tag format looks like this,
        <function=function_name>(parameters)</function>

    The detailed prompts for each of these formats are defined in `system_prompt.py`
    """

    json = "json"
    function_tag = "function_tag"


@json_schema_type
class AgenticSystemInstanceConfig(BaseModel):
    instructions: str
    sampling_params: Optional[SamplingParams] = SamplingParams()
    # zero-shot or built-in tool configurations as input to the model
    available_tools: Optional[List[AgenticSystemToolDefinition]] = Field(
        default_factory=list
    )

    input_shields: Optional[List[ShieldDefinition]] = Field(default_factory=list)
    output_shields: Optional[List[ShieldDefinition]] = Field(default_factory=list)

    # if you completely want to replace the messages prefixed by the system,
    # this is debug only
    debug_prefix_messages: Optional[List[Message]] = Field(default_factory=list)
    tool_prompt_format: Optional[ToolPromptFormat] = Field(
        default=ToolPromptFormat.json
    )


class AgenticSystemTurnResponseEventType(Enum):
    step_start = "step_start"
    step_complete = "step_complete"
    step_progress = "step_progress"

    turn_start = "turn_start"
    turn_complete = "turn_complete"


@json_schema_type
class AgenticSystemTurnResponseStepStartPayload(BaseModel):
    event_type: Literal[AgenticSystemTurnResponseEventType.step_start.value] = (
        AgenticSystemTurnResponseEventType.step_start.value
    )
    step_type: StepType
    step_id: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


@json_schema_type
class AgenticSystemTurnResponseStepCompletePayload(BaseModel):
    event_type: Literal[AgenticSystemTurnResponseEventType.step_complete.value] = (
        AgenticSystemTurnResponseEventType.step_complete.value
    )
    step_type: StepType
    step_details: Step


@json_schema_type
class AgenticSystemTurnResponseStepProgressPayload(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    event_type: Literal[AgenticSystemTurnResponseEventType.step_progress.value] = (
        AgenticSystemTurnResponseEventType.step_progress.value
    )
    step_type: StepType
    step_id: str

    model_response_text_delta: Optional[str] = None
    tool_call_delta: Optional[ToolCallDelta] = None
    tool_response_text_delta: Optional[str] = None


@json_schema_type
class AgenticSystemTurnResponseTurnStartPayload(BaseModel):
    event_type: Literal[AgenticSystemTurnResponseEventType.turn_start.value] = (
        AgenticSystemTurnResponseEventType.turn_start.value
    )
    turn_id: str


@json_schema_type
class AgenticSystemTurnResponseTurnCompletePayload(BaseModel):
    event_type: Literal[AgenticSystemTurnResponseEventType.turn_complete.value] = (
        AgenticSystemTurnResponseEventType.turn_complete.value
    )
    turn: Turn


@json_schema_type
class AgenticSystemTurnResponseEvent(BaseModel):
    """Streamed agent execution response."""

    payload: Annotated[
        Union[
            AgenticSystemTurnResponseStepStartPayload,
            AgenticSystemTurnResponseStepProgressPayload,
            AgenticSystemTurnResponseStepCompletePayload,
            AgenticSystemTurnResponseTurnStartPayload,
            AgenticSystemTurnResponseTurnCompletePayload,
        ],
        Field(discriminator="event_type"),
    ]
