from typing import List

from .models import Graph, GraphStats, DocumentMeta, QueryRequest, IngestDocumentRequest


class ArtifactGraph(Graph):
    @classmethod
    def from_graph(cls, client_or_api, graph: Graph) -> "ArtifactGraph":
        if not isinstance(graph, Graph):
            raise RuntimeError(f"Expected graph to be instance of {cls}, got {type(graph)}")
        return cls(client_or_api, **graph.to_dict())

    def __init__(self, client_or_api, uuid=None, **kwargs):
        # this class serves no purpose without being able to make remote calls
        if client_or_api is None:
            raise RuntimeError("ArtifactClient or DefaultApi is required")

        # existing graph is required to instantiate this class. uuid is a kwarg so that it can
        # be included in a dict of graph attributes more easily for the caller
        if not uuid:
            raise RuntimeError("Existing graph is required to instantiate this class")

        # avoid circular imports
        from .api import DefaultApi
        from .artifact_client import ArtifactClient

        if isinstance(client_or_api, DefaultApi):
            self.api_instance = client_or_api
        elif isinstance(client_or_api, ArtifactClient):
            self.api_instance = client_or_api.api_instance
        else:
            raise RuntimeError(
                f"Expected client_or_api to be instance of {DefaultApi} or {ArtifactClient}, got {type(client_or_api)}"
            )

        # for caller convenience, allow uuid only to be specified and retrieve the rest of the graph data remotely
        if not kwargs:
            graph = self.api_instance.get_graph(graph_id=uuid)
            kwargs = graph.to_dict()

        super().__init__(uuid=uuid, **kwargs)
        if not self.uuid:
            raise RuntimeError("Graph uuid is required")

    def sync(self):
        self._check_deleted()
        graph = self.api_instance.get_graph(graph_id=self.uuid)
        self._update(**graph.to_dict())

    def update(self, **attrs):
        self._check_deleted()
        self.api_instance.update_graph(graph_id=self.uuid, graph_update_request=attrs)
        self.sync()

    def ingest(self, document: str) -> None:
        """Ingest a document into the graph."""
        self._check_deleted()
        body = IngestDocumentRequest(document=document)
        resp = self.api_instance.api_instance.ingest_document(graph_id=self.uuid, ingest_document_request=body)
        self.sync()
        return resp

    def query(self, query: str) -> str:
        """Query the graph."""
        self._check_deleted()
        body = QueryRequest(query=query)
        return self.api_instance.api_instance.query_graph(graph_id=self.uuid, query_request=body)

    def stats(self) -> GraphStats:
        """Get graph statistics."""
        self._check_deleted()
        return self.api_instance.api_instance.get_graph_stats(graph_id=self.uuid)

    def documents_meta(self) -> List[DocumentMeta]:
        """Get documents metadata."""
        self._check_deleted()
        return self.api_instance.api_instance.get_graph_documents_meta(graph_id=self.uuid)

    def delete(self) -> None:
        """Delete a graph."""
        self._check_deleted()
        response = self.api_instance.api_instance.delete_graph(graph_id=self.uuid)
        return response

    def _update(self, attrs: dict):
        # only one graph per instance
        graph_id = attrs.get("uuid", self.uuid)
        if not graph_id or graph_id != self.uuid:
            raise RuntimeError(f"Changing associated graph from {self.uuid} to {graph_id} is not allowed")
        # TODO: validate data. don't blindly set attributes
        for k, v in attrs.items():
            setattr(self, k, v)

    def _check_deleted(self) -> False:
        # uuid created in constructor. only time for it to be None is after a delete operation
        if not self.uuid:
            raise RuntimeError(f"Access attempted on deleted graph")
