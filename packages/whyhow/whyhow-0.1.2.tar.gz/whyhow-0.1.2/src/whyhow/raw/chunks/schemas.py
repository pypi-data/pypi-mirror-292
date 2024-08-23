"""Collection of Pydantic models for the the chunks router."""

from typing import Literal

from whyhow.raw.autogen import (
    ChunkMetadata,
    ChunksOutWithWorkspaceDetails,
    ChunksResponseWithWorkspaceDetails,
    DocumentDetail,
    WorkspaceDetails,
)
from whyhow.raw.base import PathParameters, QueryParameters, ResponseBody

# Auxiliary models
ChunkWorkspaceRaw = WorkspaceDetails
ChunkDocumentDetailRaw = DocumentDetail
ChunkMetadataRaw = ChunkMetadata
ChunkRaw = ChunksOutWithWorkspaceDetails


# GET /chunks/{chunk_id}
class GetChunkPathParameters(PathParameters):
    """Path parameters for the get chunk endpoint."""

    chunk_id: str


class GetChunkQueryParameters(QueryParameters):
    """Query parameters for the get chunk endpoint."""

    include_embeddings: bool | None = None


class GetChunkResponseBody(ResponseBody, ChunksResponseWithWorkspaceDetails):
    """Response body for the get chunk endpoint."""


# GET /chunks
class GetAllChunksQueryParameters(QueryParameters):
    """Query parameters for the get all chunks endpoint."""

    skip: int | None = None
    limit: int | None = None
    data_type: str | None = None
    workspace_id: str | None = None
    workspace_name: str | None = None
    worskpace_id: str | None = None
    document_id: str | None = None
    document_filename: str | None = None
    include_embeddings: bool | None = None
    order: Literal["ascending", "descending"] | None = None


class GetAllChunksResponseBody(
    ResponseBody, ChunksResponseWithWorkspaceDetails
):
    """Response body for the get all chunks endpoint."""
