from __future__ import annotations

import os
import json
import logging
from typing import Any, List, TypeVar, Callable, Optional, Protocol

from .utils import extract_body, upload_file_to_presigned_s3
from .client import DefaultApi
from .errors import (
    ApiException,
    ServiceException,
    NotFoundException,
    UnauthorizedException,
    GraphAlreadyExistsException,
)
from .models import (
    Graph,
    DocumentMeta,
    QueryRequest,
    PresignRequest,
    PresignResponse,
    CreateGraphRequest,
    IngestDocumentRequest,
)
from .artifact_graph import ArtifactGraph

log = logging.getLogger(__name__)

T = TypeVar("T")


class ErrorResponse(Protocol):
    error_type: str
    message: str


def _raise_error(error) -> None:
    if error.error_type == "UNAUTHORIZED":
        raise UnauthorizedException(error.message)
    elif error.error_type == "NOT_FOUND":
        raise NotFoundException(error.message)
    elif error.error_type == "INTERNAL_ERROR":
        raise ServiceException(error.message)
    elif error.error_type == "GRAPH_ALREADY_EXISTS":
        raise GraphAlreadyExistsException(error.message)
    else:
        raise ApiException(error.message)


def _safe_request(api_call: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    response = api_call(*args, **kwargs)
    if hasattr(response, "error_type"):
        _raise_error(response)
    return response


class ArtifactClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        api_key = api_key or os.environ.get("ARTIFACT_API_KEY")
        if api_key is None:
            raise RuntimeError(
                "API authorization key required. "
                "Set ARTIFACT_API_KEY environment variable or pass as argument to client."
            )
        base_url = base_url or os.environ.get("ARTIFACT_BASE_URL", "https://api.useartifact.ai")

        from .client import ApiClient, Configuration

        config = Configuration()
        if base_url:
            config.host = base_url
        # config.api_key = {"Authorization": api_key}
        # Configure API key authorization: ApiKeyAuth
        config.api_key["ApiKeyAuth"] = api_key

        api = ApiClient(configuration=config)
        self.api_instance = DefaultApi(api_client=api)
        self.api_key = api_key

    @property
    def api(self):
        return self.api_instance.api_client

    @property
    def configuration(self):
        return self.api.configuration

    @property
    def num_graphs(self):
        try:
            return len(self.list_all_graphs())
        except (ApiException, RuntimeError) as e:
            log.error(f"List all graphs failed with exception: {e}")
            return 0

    def list_all_graphs(self) -> List[Graph]:
        """Lists all graphs."""
        return self.api_instance.list_graphs()

    def delete_all_graphs(self):
        """Delete all graphs associated with the organization"""
        response = self.api_instance.delete_all_graphs()
        return response

    def create_graph(self, name: str, index_interval: str = "IMMEDIATE") -> Graph:
        """
        Create a new graph.

        :param name: Name of the graph
        :param index_interval: Indexing interval (default: "IMMEDIATE")
        :return: Graph object
        :raises GraphAlreadyExistsError: If a graph with the given name already exists (201)
        :raises UnauthorizedError: If the API key is invalid (401)
        :raises ValidationError: If the input parameters are invalid
        :raises ApiException: Base exception covering other API-related errors
        """
        return _safe_request(
            self.api_instance.create_graph, CreateGraphRequest(name=name, index_interval=index_interval)
        )

    def Graph(self, name: str, index_interval: str = "IMMEDIATE") -> "ArtifactGraph":
        graph = self.create_graph(name, index_interval=index_interval)
        return ArtifactGraph.from_graph(self, graph)

    def get_graph(self, graph_name: str) -> Graph:
        return _safe_request(self.api_instance.get_graph, graph_name)

    def update_graph(self, graph_name: str, **attrs) -> Graph:
        """Update a graph."""
        if attrs.get("name", graph_name) != graph_name:
            raise ValueError(f"graph_name arg {graph_name} inconsistent with attrs {attrs['name']}")
        attrs["name"] = graph_name
        return _safe_request(self.api_instance.update_graph, graph_name, Graph.from_dict(attrs))

    def delete_graph(self, graph_name: str):
        """Delete a graph."""
        _safe_request(self.api_instance.delete_graph, graph_name)

    def index_graph(self, graph_name: str):
        _safe_request(self.api_instance.index_graph, graph_name)

    def query_graph(self, graph_name: str, query: str):
        """Query the graph."""
        try:
            return _safe_request(self.api_instance.query_graph, graph_name, QueryRequest(query=query))
        except (ApiException, RuntimeError) as e:
            # api returns cryptic error when graph isn't ready to be queried
            try:
                body = extract_body(e)
            except Exception:
                body = {}
            if body and "responseText" in body:
                msg_data = json.loads(body["responseText"])
                if "detail" in msg_data and "EFS mount path does not exist" in msg_data.get("detail", {}):
                    log.error(f"Graph {graph_name} is not ready to be queried. Try again later.")
                    return None
            raise e

    def graph_stats(self, graph_name: str):
        """Get graph statistics."""
        return _safe_request(self.api_instance.get_graph_stats, graph_name)

    def ingest_document(self, graph_name: str, document: str):
        """Ingest a document into the graph."""
        return _safe_request(self.api_instance.ingest_document, graph_name, IngestDocumentRequest(document=document))

    def ingest_file(self, graph_name: str, file_path: str):
        """Ingest a file into the graph."""
        if not os.path.exists(file_path):
            raise RuntimeError(f"File {file_path} does not exist")

        resp: PresignResponse = _safe_request(
            self.api_instance.presign_graph, graph_name, PresignRequest(file_name=os.path.split(file_path)[1])
        )
        meta = upload_file_to_presigned_s3(file_path, resp.presigned_url)
        if not meta:
            raise RuntimeError(f"Unable to upload file {file_path} to S3 from response {resp}")
        return meta

    def get_document_meta(self, graph_name: str) -> List[DocumentMeta]:
        """Get documents metadata."""
        return _safe_request(self.api_instance.get_graph_documents_meta, graph_name=graph_name)
