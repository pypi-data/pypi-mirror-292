# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from .code_interpreter_tool_param import CodeInterpreterToolParam
from .threads.message_content_part_param import MessageContentPartParam

__all__ = [
    "ThreadCreateParams",
    "Message",
    "MessageAttachment",
    "MessageAttachmentTool",
    "MessageAttachmentToolFileSearch",
    "ToolResources",
    "ToolResourcesCodeInterpreter",
    "ToolResourcesFileSearch",
    "ToolResourcesFileSearchVectorStore",
    "ToolResourcesFileSearchVectorStoreChunkingStrategy",
    "ToolResourcesFileSearchVectorStoreChunkingStrategyAuto",
    "ToolResourcesFileSearchVectorStoreChunkingStrategyStatic",
    "ToolResourcesFileSearchVectorStoreChunkingStrategyStaticStatic",
]


class ThreadCreateParams(TypedDict, total=False):
    messages: Iterable[Message]
    """
    A list of [messages](https://platform.openai.com/docs/api-reference/messages) to
    start the thread with.
    """

    metadata: Optional[object]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format. Keys can be a maximum of 64 characters long and values can be
    a maxium of 512 characters long.
    """

    tool_resources: Optional[ToolResources]
    """
    A set of resources that are made available to the assistant's tools in this
    thread. The resources are specific to the type of tool. For example, the
    `code_interpreter` tool requires a list of file IDs, while the `file_search`
    tool requires a list of vector store IDs.
    """


class MessageAttachmentToolFileSearch(TypedDict, total=False):
    type: Required[Literal["file_search"]]
    """The type of tool being defined: `file_search`"""


MessageAttachmentTool = Union[CodeInterpreterToolParam, MessageAttachmentToolFileSearch]


class MessageAttachment(TypedDict, total=False):
    file_id: str
    """The ID of the file to attach to the message."""

    tools: Iterable[MessageAttachmentTool]
    """The tools to add this file to."""


class Message(TypedDict, total=False):
    content: Required[Union[str, Iterable[MessageContentPartParam]]]
    """The text contents of the message."""

    role: Required[Literal["user", "assistant"]]
    """The role of the entity that is creating the message. Allowed values include:

    - `user`: Indicates the message is sent by an actual user and should be used in
      most cases to represent user-generated messages.
    - `assistant`: Indicates the message is generated by the assistant. Use this
      value to insert messages from the assistant into the conversation.
    """

    attachments: Optional[Iterable[MessageAttachment]]
    """A list of files attached to the message, and the tools they should be added to."""

    metadata: Optional[object]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format. Keys can be a maximum of 64 characters long and values can be
    a maxium of 512 characters long.
    """


class ToolResourcesCodeInterpreter(TypedDict, total=False):
    file_ids: List[str]
    """
    A list of [file](https://platform.openai.com/docs/api-reference/files) IDs made
    available to the `code_interpreter` tool. There can be a maximum of 20 files
    associated with the tool.
    """


class ToolResourcesFileSearchVectorStoreChunkingStrategyAuto(TypedDict, total=False):
    type: Required[Literal["auto"]]
    """Always `auto`."""


class ToolResourcesFileSearchVectorStoreChunkingStrategyStaticStatic(TypedDict, total=False):
    chunk_overlap_tokens: Required[int]
    """The number of tokens that overlap between chunks. The default value is `400`.

    Note that the overlap must not exceed half of `max_chunk_size_tokens`.
    """

    max_chunk_size_tokens: Required[int]
    """The maximum number of tokens in each chunk.

    The default value is `800`. The minimum value is `100` and the maximum value is
    `4096`.
    """


class ToolResourcesFileSearchVectorStoreChunkingStrategyStatic(TypedDict, total=False):
    static: Required[ToolResourcesFileSearchVectorStoreChunkingStrategyStaticStatic]

    type: Required[Literal["static"]]
    """Always `static`."""


ToolResourcesFileSearchVectorStoreChunkingStrategy = Union[
    ToolResourcesFileSearchVectorStoreChunkingStrategyAuto, ToolResourcesFileSearchVectorStoreChunkingStrategyStatic
]


class ToolResourcesFileSearchVectorStore(TypedDict, total=False):
    chunking_strategy: ToolResourcesFileSearchVectorStoreChunkingStrategy
    """The chunking strategy used to chunk the file(s).

    If not set, will use the `auto` strategy.
    """

    file_ids: List[str]
    """
    A list of [file](https://platform.openai.com/docs/api-reference/files) IDs to
    add to the vector store. There can be a maximum of 10000 files in a vector
    store.
    """

    metadata: object
    """Set of 16 key-value pairs that can be attached to a vector store.

    This can be useful for storing additional information about the vector store in
    a structured format. Keys can be a maximum of 64 characters long and values can
    be a maxium of 512 characters long.
    """


class ToolResourcesFileSearch(TypedDict, total=False):
    vector_store_ids: List[str]
    """
    The
    [vector store](https://platform.openai.com/docs/api-reference/vector-stores/object)
    attached to this thread. There can be a maximum of 1 vector store attached to
    the thread.
    """

    vector_stores: Iterable[ToolResourcesFileSearchVectorStore]
    """
    A helper to create a
    [vector store](https://platform.openai.com/docs/api-reference/vector-stores/object)
    with file_ids and attach it to this thread. There can be a maximum of 1 vector
    store attached to the thread.
    """


class ToolResources(TypedDict, total=False):
    code_interpreter: ToolResourcesCodeInterpreter

    file_search: ToolResourcesFileSearch
