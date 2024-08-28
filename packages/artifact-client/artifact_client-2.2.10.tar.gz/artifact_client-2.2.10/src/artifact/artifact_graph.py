import logging
from typing import List

from .models import Graph, GraphStats, DocumentMeta

log = logging.getLogger(__name__)


class ArtifactGraph(Graph):
    @classmethod
    def from_graph(cls, client, graph: Graph) -> "ArtifactGraph":
        if not isinstance(graph, Graph):
            raise RuntimeError(f"Expected graph to be instance of {cls}, got {type(graph)}")
        return cls(client, **graph.to_dict())

    def __init__(self, client, name=None, **attrs):
        """

        :param client:
        :param name: Name of existing graph
        :param attrs: When specified, they populate this local graph instance.  It is the caller's responsibility
            to ensure that they are consistent with the remote graph. When no attributes ar e specified, the remote
            graph is downloaded and used to populate this instance.
        """
        # avoid circular imports
        from .artifact_client import ArtifactClient

        # create default client. this assumes that the api key is in the env
        if client is None:
            client = ArtifactClient()

        # existing graph is required to instantiate this class. uuid is a kwarg so that it can
        # be included in a dict of graph attributes more easily for the caller
        if not name:
            raise RuntimeError("Existing graph is required to instantiate this class")

        if not isinstance(client, ArtifactClient):
            raise RuntimeError(f"Expected ArtifactClient, got {type(client)}")

        # for caller convenience, allow name only to be specified and retrieve the rest of the graph data remotely
        if not attrs:
            # if graph doesn't exist, exception will be thrown
            attrs = client.get_graph(name).to_dict()

        super().__init__(name=name, **attrs)
        self._client = client
        self._deleted = False

    @property
    def client(self):
        return self._client

    @property
    def deleted(self):
        return self._deleted

    @property
    def stats(self) -> GraphStats:
        """Get graph statistics."""
        self._check_deleted()
        return self._client.graph_stats(self.name)

    @property
    def documents_meta(self) -> List[DocumentMeta]:
        """Get documents metadata."""
        self._check_deleted()
        return self._client.get_document_meta(self.name)

    @deleted.setter
    def deleted(self, value):
        # latching condition
        if self._deleted and not value:
            log.warning(f"Once graph {self.name} is deleted, this instance must be discarded")
        self._deleted = value

    def sync(self):
        self._check_deleted()
        graph = self._client.get_graph(self.name)
        self._update(graph.to_dict())

    def update(self, **attrs):
        self._check_deleted()
        updated_graph = self._client.update_graph(self.name, **attrs)
        self._update(updated_graph.to_dict())

    def ingest(self, document: str) -> None:
        """Ingest a document into the graph."""
        self._check_deleted()
        resp = self._client.ingest_document(self.name, document)
        self.sync()
        return resp

    def query(self, query: str) -> str:
        """Query the graph."""
        self._check_deleted()
        return self._client.query_graph(self.name, query)

    def delete(self) -> None:
        """Delete a graph. This is latching and disables all other operations.
        The client is still accessible for use in a new instance, if needed."""
        self._check_deleted()
        self._client.delete_graph(self.name)
        self.deleted = True

    def _update(self, attrs: dict):
        # only one graph per instance
        g_name = attrs.get("name", self.name)
        if not g_name or g_name != self.name:
            raise RuntimeError(f"Changing associated graph from {self.name} to {g_name} is not allowed")
        # TODO: validate data. don't blindly set attributes
        for k, v in attrs.items():
            setattr(self, k, v)

    def _check_deleted(self):
        if self.deleted:
            raise RuntimeError(f"Access attempted on deleted graph with name {self.name}")
