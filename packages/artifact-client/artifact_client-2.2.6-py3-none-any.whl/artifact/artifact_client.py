import os
import json
import logging
from typing import List, Optional

from .utils import extract_body, upload_file_to_presigned_s3
from .client import DefaultApi
from .models import (
    Graph,
    GraphStats,
    ApiException,
    DocumentMeta,
    QueryRequest,
    PresignRequest,
    PresignResponse,
    CreateGraphRequest,
    IngestDocumentRequest,
)

log = logging.getLogger(__name__)


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
        """Create a new graph."""
        return self.api_instance.create_graph(CreateGraphRequest(name=name, index_interval=index_interval))  # type: ignore

    def get_graph(self, graph_name: str) -> Graph:
        return self.api_instance.get_graph(graph_name)  # type: ignore

    def update_graph(self, graph_name: str, **attrs) -> Graph:
        """Update a graph."""
        return self.api_instance.update_graph(graph_name, Graph.from_dict(attrs))  # type: ignore

    def delete_graph(self, graph_name: str):
        """Delete a graph."""
        self.api_instance.delete_graph(graph_name)

    def index_graph(self, graph_name: str):
        self.api_instance.index_graph(graph_name)

    def query_graph(self, graph_name: str, query: str) -> Optional[str]:
        """Query the graph."""
        try:
            return self.api_instance.query_graph(graph_name, QueryRequest(query=query))  # type: ignore
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

    def graph_stats(self, graph_name: str) -> GraphStats:
        """Get graph statistics."""
        return self.api_instance.get_graph_stats(graph_name)  # type: ignore

    def ingest_document(self, graph_name: str, document: str) -> None:
        """Ingest a document into the graph."""
        return self.api_instance.ingest_document(graph_name, IngestDocumentRequest(document=document))  # type: ignore

    def ingest_file(self, graph_name: str, file_path: str):
        """Ingest a file into the graph."""
        if not os.path.exists(file_path):
            raise RuntimeError(f"File {file_path} does not exist")

        resp: PresignResponse = self.api_instance.presign_graph(
            graph_name, PresignRequest(file_name=os.path.split(file_path)[1])
        )
        meta = upload_file_to_presigned_s3(file_path, resp.presigned_url)
        if not meta:
            raise RuntimeError(f"Unable to upload file {file_path} to S3 from response {resp}")
        return meta

    def get_document_meta(self, graph_name: str) -> List[DocumentMeta]:
        """Get documents metadata."""
        return self.api_instance.get_graph_documents_meta(graph_name=graph_name)  # type: ignore
