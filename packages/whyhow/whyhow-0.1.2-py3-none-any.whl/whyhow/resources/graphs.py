"""Graph resources."""

from typing import Any, AsyncIterator, Iterator, Literal

from whyhow.raw import (
    CreateGraphFromTriplesRequestBody,
    CreateGraphRequestBody,
    GraphChunkFiltersRaw,
    TripleRaw,
    acreate_graph,
    acreate_graph_from_triples,
    aexport_graph_cypher,
    aget_all_graphs,
    aget_all_triples,
    aget_graph,
    aquery_graph_structured,
    aquery_graph_unstructured,
    aupdate_graph,
    create_graph,
    create_graph_from_triples,
    export_graph_cypher,
    get_all_graphs,
    get_all_triples,
    get_graph,
    query_graph_structured,
    query_graph_unstructured,
    update_graph,
)
from whyhow.resources.base import AsyncResource, Resource, validate
from whyhow.schemas import (
    Graph,
    GraphErrorDetails,
    Node,
    Query,
    Relation,
    Triple,
)

VALID_DATA_TYPE = Literal["string", "object"]
CREATION_MODE = Literal["unstructured", "structured", "mixed"]


class GraphsResource(Resource):
    """Graph resources."""

    def get(self, graph_id: str) -> Graph:
        """
        Get a graph by its ID.

        Parameters
        ----------
        graph_id : str
            The ID of the graph.

        Returns
        -------
        Graph
            The graph.
        """
        result = get_graph(self.client, graph_id)

        body = validate(result)

        raw_graph = body.graphs[0]

        if raw_graph.errors is None:
            errors = None
        else:
            errors = [
                GraphErrorDetails(**error.model_dump())
                for error in raw_graph.errors
            ]

        graph = Graph(
            graph_id=raw_graph.field_id,
            name=raw_graph.name,
            workspace_id=raw_graph.workspace.field_id,
            created_at=raw_graph.created_at,
            updated_at=raw_graph.updated_at,
            schema_id=raw_graph.schema_.field_id,
            status=raw_graph.status,
            errors=errors,
            public=raw_graph.public,
        )

        return graph

    def get_all(
        self,
        limit: int = 10,
        name: str | None = None,
        workspace_id: str | None = None,
        workspace_name: str | None = None,
        schema_id: str | None = None,
        schema_name: str | None = None,
    ) -> Iterator[Graph]:
        """
        Get all graphs.

        Parameters
        ----------
        limit : int, optional
            The number of graphs to return.
        name : str, optional
            The name of the graph.
        workspace_id : str, optional
            The ID of the workspace.
        workspace_name : str, optional
            The name of the workspace.
        schema_id : str, optional
            The ID of the schema.
        schema_name : str, optional
            The name of the schema.

        Returns
        -------
        Iterator[Graph]
            The graph iterator.

        Yields
        ------
        Graph
            The graph.
        """
        skip = 0

        while True:
            result = get_all_graphs(
                self.client,
                skip=skip,
                limit=limit,
                name=name,
                workspace_id=workspace_id,
                workspace_name=workspace_name,
                schema_id=schema_id,
                schema_name=schema_name,
            )

            body = validate(result)

            for raw_graph in body.graphs:
                skip += 1
                if raw_graph.errors is None:
                    errors = None
                else:
                    errors = [
                        GraphErrorDetails(**error.model_dump())
                        for error in raw_graph.errors
                    ]

                graph = Graph(
                    graph_id=raw_graph.field_id,
                    name=raw_graph.name,
                    workspace_id=raw_graph.workspace.field_id,
                    created_at=raw_graph.created_at,
                    updated_at=raw_graph.updated_at,
                    schema_id=raw_graph.schema_.field_id,
                    status=raw_graph.status,
                    errors=errors,
                    public=raw_graph.public,
                )

                yield graph

            if len(body.graphs) < limit:
                break

    def create(
        self,
        name: str,
        workspace_id: str,
        schema_id: str,
        mode: CREATION_MODE = "unstructured",
        document_ids: list[str] | None = None,
    ) -> Graph:
        """
        Create a graph.

        Parameters
        ----------
        name : str
            The name of the graph.
        workspace_id : str
            The ID of the workspace.
        schema_id : str
            The ID of the schema.
        mode : Literal["unstructured", "structured", "mixed"], optional
            The creation mode.
        document_ids : list[str], optional
            The IDs of the documents.

        Returns
        -------
        Graph
            The graph.
        """
        if mode == "unstructured":
            data_types: list[VALID_DATA_TYPE] | None = ["string"]
        elif mode == "structured":
            data_types = ["object"]
        else:
            data_types = None

        filters = GraphChunkFiltersRaw(
            data_types=data_types,
            document_ids=document_ids,
            ids=None,
            tags=None,
            user_metadata=None,
        )

        request_body = CreateGraphRequestBody(
            name=name,
            workspace=workspace_id,
            schema=schema_id,  # type: ignore[call-arg]
            filters=filters,
        )
        result = create_graph(self.client, request_body)

        body = validate(result)

        raw_graph = body.graphs[0]

        if raw_graph.errors is None:
            errors = None
        else:
            errors = [
                GraphErrorDetails(**error.model_dump())
                for error in raw_graph.errors
            ]

        graph = Graph(
            graph_id=raw_graph.field_id,
            name=raw_graph.name,
            workspace_id=raw_graph.field_id,
            created_at=raw_graph.created_at,
            updated_at=raw_graph.updated_at,
            schema_id=raw_graph.schema_id,
            status=raw_graph.status,
            errors=errors,
            public=raw_graph.public,
        )

        return graph

    def update(
        self,
        graph_id: str,
        name: str | None = None,
        public: bool | None = None,
    ) -> Graph:
        """
        Update a graph.

        Parameters
        ----------
        graph_id : str
            The ID of the graph.
        name : str, optional
            The name of the graph.
        public : bool, optional
            Whether the graph is public.

        Returns
        -------
        Graph
            The graph.
        """
        result = update_graph(self.client, graph_id, name=name, public=public)

        body = validate(result)

        raw_graph = body.graphs[0]

        if raw_graph.errors is None:
            errors = None
        else:
            errors = [
                GraphErrorDetails(**error.model_dump())
                for error in raw_graph.errors
            ]

        graph = Graph(
            graph_id=raw_graph.field_id,
            name=raw_graph.name,
            workspace_id=raw_graph.field_id,
            created_at=raw_graph.created_at,
            updated_at=raw_graph.updated_at,
            schema_id=raw_graph.schema_id,
            status=raw_graph.status,
            errors=errors,
            public=raw_graph.public,
        )

        return graph

    def export_cypher(self, graph_id: str) -> str:
        """
        Export a graph to Cypher.

        Parameters
        ----------
        graph_id : str
            The ID of the graph.

        Returns
        -------
        str
            The Cypher text.
        """
        result = export_graph_cypher(self.client, graph_id)

        body = validate(result)

        return body.cypher_text

    def query_unstructured(
        self,
        graph_id: str,
        query: str,
        return_answer: bool = True,
        include_chunks: bool = False,
    ) -> Query:
        """
        Unstructured query.

        Parameters
        ----------
        graph_id : str
            The ID of the graph.
        query : str
            The query.
        return_answer : bool, optional
            Whether to return the answer.
        include_chunks : bool, optional
            Whether to include chunks.

        Returns
        -------
        Query
            The query.

        Raises
        ------
        ValueError
            If no queries are found in the response body.
        """
        result = query_graph_unstructured(
            self.client,
            graph_id=graph_id,
            query=query,
            return_answer=return_answer,
            include_chunks=include_chunks,
        )

        body = validate(result)

        if body.queries is None:
            raise ValueError("No queries found in response body")

        query_raw = body.queries[0]
        nodes = [
            Node(
                node_id=raw_node.field_id,
                label=(
                    raw_node.label.root if raw_node.label is not None else ""
                ),
                name=raw_node.name,
                chunk_ids=(
                    raw_node.chunks if raw_node.chunks is not None else []
                ),
                properties=raw_node.properties,
            )
            for raw_node in (
                query_raw.nodes if query_raw.nodes is not None else []
            )
        ]

        relations = [
            Relation(
                name=raw_triple.relation.name,
                properties=raw_triple.relation.properties,
            )
            for raw_triple in (query_raw.triples if query_raw.triples else [])
        ]

        # nodes are uniquely determined by their ids (if id not present then name + label)
        id2node = {node.node_id: node for node in nodes}

        # relations are uniquely determined by their names
        name2relation = {relation.name: relation for relation in relations}

        triples = [
            Triple(
                triple_id=raw_triple.field_id,
                head=id2node[raw_triple.head_node.field_id],
                tail=id2node[raw_triple.tail_node.field_id],
                relation=name2relation[raw_triple.relation.name],
                chunk_ids=raw_triple.chunks,
            )
            for raw_triple in (query_raw.triples if query_raw.triples else [])
        ]

        retval = Query(
            query_id=query_raw.field_id,
            graph_id=query_raw.graph,
            answer=(
                query_raw.response.root
                if query_raw.response is not None
                else None
            ),
            status=query_raw.status,
            created_at=query_raw.created_at,
            updated_at=query_raw.updated_at,
            nodes=nodes,
            triples=triples,
        )

        return retval

    def query_structured(
        self,
        graph_id: str,
        entities: list[str] | None = None,
        relations: list[str] | None = None,
        values: list[str] | None = None,
    ) -> Query:
        """Structured query."""
        result = query_graph_structured(
            self.client,
            graph_id=graph_id,
            entities=entities,
            relations=relations,
            values=values,
        )

        body = validate(result)

        if body.queries is None:
            raise ValueError("No queries found in response body")

        query_raw = body.queries[0]
        nodes = [
            Node(
                node_id=raw_node.field_id,
                label=(
                    raw_node.label.root if raw_node.label is not None else ""
                ),
                name=raw_node.name,
                chunk_ids=(
                    raw_node.chunks if raw_node.chunks is not None else []
                ),
                properties=raw_node.properties,
            )
            for raw_node in (
                query_raw.nodes if query_raw.nodes is not None else []
            )
        ]

        relations_ = [
            Relation(
                name=raw_triple.relation.name,
                properties=raw_triple.relation.properties,
            )
            for raw_triple in (query_raw.triples if query_raw.triples else [])
        ]

        # nodes are uniquely determined by their ids (if id not present then name + label)
        id2node = {node.node_id: node for node in nodes}

        # relations are uniquely determined by their names
        name2relation = {relation.name: relation for relation in relations_}

        triples = [
            Triple(
                triple_id=raw_triple.field_id,
                head=id2node[raw_triple.head_node.field_id],
                tail=id2node[raw_triple.tail_node.field_id],
                relation=name2relation[raw_triple.relation.name],
                chunk_ids=raw_triple.chunks,
            )
            for raw_triple in (query_raw.triples if query_raw.triples else [])
        ]

        retval = Query(
            query_id=query_raw.field_id,
            graph_id=query_raw.graph,
            answer=(
                query_raw.response.root
                if query_raw.response is not None
                else None
            ),
            status=query_raw.status,
            created_at=query_raw.created_at,
            updated_at=query_raw.updated_at,
            nodes=nodes,
            triples=triples,
        )

        return retval

    def get_all_triples(
        self,
        graph_id: str,
        limit: int = 10,
    ) -> Iterator[Triple]:
        """
        Get all triples.

        Parameters
        ----------
        graph_id : str
            The ID of the graph.
        limit : int, optional
            The number of triples to return.

        Returns
        -------
        Iterator[Triple]
            The triple iterator.

        Yields
        ------
        Triple
            The triple.
        """
        skip = 0

        while True:
            result = get_all_triples(
                self.client,
                graph_id=graph_id,
                skip=skip,
                limit=limit,
            )

            body = validate(result)

            if body.triples is None:
                return

            for raw_triple in body.triples:
                skip += 1

                triple = Triple(
                    triple_id=raw_triple.field_id,
                    head=Node(
                        node_id=raw_triple.head_node.field_id,
                        label=(
                            raw_triple.head_node.label.root
                            if raw_triple.head_node.label is not None
                            else ""
                        ),
                        name=raw_triple.head_node.name,
                        chunk_ids=(
                            raw_triple.head_node.chunks
                            if raw_triple.head_node.chunks is not None
                            else []
                        ),
                        properties=raw_triple.head_node.properties,
                    ),
                    tail=Node(
                        node_id=raw_triple.tail_node.field_id,
                        label=(
                            raw_triple.tail_node.label.root
                            if raw_triple.tail_node.label is not None
                            else ""
                        ),
                        name=raw_triple.tail_node.name,
                        chunk_ids=(
                            raw_triple.tail_node.chunks
                            if raw_triple.tail_node.chunks is not None
                            else []
                        ),
                        properties=raw_triple.tail_node.properties,
                    ),
                    relation=Relation(
                        name=raw_triple.relation.name,
                        properties=raw_triple.relation.properties,
                    ),
                    chunk_ids=raw_triple.chunks,
                )

                yield triple

            if len(body.triples) < limit:
                break

    def create_graph_from_triples(
        self,
        name: str,
        workspace_id: str,
        triples: list[Triple],
        schema_id: str | None = None,
    ) -> Graph:
        """
        Create a graph from triples.

        Parameters
        ----------
        name : str
            The name of the graph.
        workspace_id : str
            The ID of the workspace.
        triples : list[Triple]
            The triples.
        schema_id : str, optional
            The ID of the schema. If not provided, the schema will be inferred.

        Returns
        -------
        Graph
            The graph.
        """
        triples_raw: list[TripleRaw] = []

        for triple in triples:
            # head properties
            head_properties: dict[str, Any] = {}

            if isinstance(triple.head.properties, dict):
                head_properties.update(triple.head.properties)

            if triple.head.chunk_ids is not None:
                head_properties["chunks"] = triple.head.chunk_ids

            # tail properties
            tail_properties: dict[str, Any] = {}

            if isinstance(triple.tail.properties, dict):
                tail_properties.update(triple.tail.properties)

            if triple.tail.chunk_ids is not None:
                tail_properties["chunks"] = triple.tail.chunk_ids

            # relation properties
            relation_properties: dict[str, Any] = {}

            if isinstance(triple.relation.properties, dict):
                relation_properties.update(triple.relation.properties)

            if triple.chunk_ids is not None:
                relation_properties["chunks"] = triple.chunk_ids

            triple_raw = TripleRaw(
                head=triple.head.name,
                head_type=triple.head.label,
                relation=triple.relation.name,
                tail=triple.tail.name,
                tail_type=triple.tail.label,
                head_properties=head_properties,
                tail_properties=tail_properties,
                relation_properties=relation_properties,
            )

            triples_raw.append(triple_raw)

        request_body = CreateGraphFromTriplesRequestBody(
            name=name,
            workspace=workspace_id,
            schema=schema_id,  # type: ignore[call-arg]
            triples=triples_raw,
        )

        result = create_graph_from_triples(self.client, body=request_body)

        body = validate(result)

        raw_graph = body.graphs[0]

        if raw_graph.errors is None:
            errors = None
        else:
            errors = [
                GraphErrorDetails(**error.model_dump())
                for error in raw_graph.errors
            ]

        graph = Graph(
            graph_id=raw_graph.field_id,
            name=raw_graph.name,
            workspace_id=raw_graph.workspace_id,
            created_at=raw_graph.created_at,
            updated_at=raw_graph.updated_at,
            schema_id=raw_graph.schema_id,
            status=raw_graph.status,
            errors=errors,
            public=raw_graph.public,
        )

        return graph


class AsyncGraphsResource(AsyncResource):
    """Graph resources."""

    async def get(self, graph_id: str) -> Graph:
        """
        Get a graph by its ID.

        Parameters
        ----------
        graph_id : str
            The ID of the graph.

        Returns
        -------
        Graph
            The graph.
        """
        result = await aget_graph(self.client, graph_id)

        body = validate(result)

        raw_graph = body.graphs[0]

        if raw_graph.errors is None:
            errors = None
        else:
            errors = [
                GraphErrorDetails(**error.model_dump())
                for error in raw_graph.errors
            ]

        graph = Graph(
            graph_id=raw_graph.field_id,
            name=raw_graph.name,
            workspace_id=raw_graph.workspace.field_id,
            created_at=raw_graph.created_at,
            updated_at=raw_graph.updated_at,
            schema_id=raw_graph.schema_.field_id,
            status=raw_graph.status,
            errors=errors,
            public=raw_graph.public,
        )

        return graph

    async def get_all(
        self,
        limit: int = 10,
        name: str | None = None,
        workspace_id: str | None = None,
        workspace_name: str | None = None,
        schema_id: str | None = None,
        schema_name: str | None = None,
    ) -> AsyncIterator[Graph]:
        """
        Get all graphs.

        Parameters
        ----------
        limit : int, optional
            The number of graphs to return.
        name : str, optional
            The name of the graph.
        workspace_id : str, optional
            The ID of the workspace.
        workspace_name : str, optional
            The name of the workspace.
        schema_id : str, optional
            The ID of the schema.
        schema_name : str, optional
            The name of the schema.

        Returns
        -------
        AsyncIterator[Graph]
            The graph iterator.

        Yields
        ------
        Graph
            The graph.
        """
        skip = 0

        while True:
            result = await aget_all_graphs(
                self.client,
                skip=skip,
                limit=limit,
                name=name,
                workspace_id=workspace_id,
                workspace_name=workspace_name,
                schema_id=schema_id,
                schema_name=schema_name,
            )

            body = validate(result)

            for raw_graph in body.graphs:
                skip += 1
                if raw_graph.errors is None:
                    errors = None
                else:
                    errors = [
                        GraphErrorDetails(**error.model_dump())
                        for error in raw_graph.errors
                    ]

                graph = Graph(
                    graph_id=raw_graph.field_id,
                    name=raw_graph.name,
                    workspace_id=raw_graph.workspace.field_id,
                    created_at=raw_graph.created_at,
                    updated_at=raw_graph.updated_at,
                    schema_id=raw_graph.schema_.field_id,
                    status=raw_graph.status,
                    errors=errors,
                    public=raw_graph.public,
                )

                yield graph

            if len(body.graphs) < limit:
                break

    async def create(
        self,
        name: str,
        workspace_id: str,
        schema_id: str,
        mode: CREATION_MODE = "unstructured",
        document_ids: list[str] | None = None,
    ) -> Graph:
        """
        Create a graph.

        Parameters
        ----------
        name : str
            The name of the graph.
        workspace_id : str
            The ID of the workspace.
        schema_id : str
            The ID of the schema.
        mode : Literal["unstructured", "structured", "mixed"], optional
            The creation mode.
        document_ids : list[str], optional
            The IDs of the documents.

        Returns
        -------
        Graph
            The graph.
        """
        if mode == "unstructured":
            data_types: list[VALID_DATA_TYPE] | None = ["string"]
        elif mode == "structured":
            data_types = ["object"]
        else:
            data_types = None

        filters = GraphChunkFiltersRaw(
            data_types=data_types,
            document_ids=document_ids,
            ids=None,
            tags=None,
            user_metadata=None,
        )

        request_body = CreateGraphRequestBody(
            name=name,
            workspace=workspace_id,
            schema=schema_id,  # type: ignore[call-arg]
            filters=filters,
        )
        result = await acreate_graph(self.client, request_body)

        body = validate(result)

        raw_graph = body.graphs[0]

        if raw_graph.errors is None:
            errors = None
        else:
            errors = [
                GraphErrorDetails(**error.model_dump())
                for error in raw_graph.errors
            ]

        graph = Graph(
            graph_id=raw_graph.field_id,
            name=raw_graph.name,
            workspace_id=raw_graph.field_id,
            created_at=raw_graph.created_at,
            updated_at=raw_graph.updated_at,
            schema_id=raw_graph.schema_id,
            status=raw_graph.status,
            errors=errors,
            public=raw_graph.public,
        )

        return graph

    async def update(
        self,
        graph_id: str,
        name: str | None = None,
        public: bool | None = None,
    ) -> Graph:
        """
        Update a graph.

        Parameters
        ----------
        graph_id : str
            The ID of the graph.
        name : str, optional
            The name of the graph.
        public : bool, optional
            Whether the graph is public.

        Returns
        -------
        Graph
            The graph.
        """
        result = await aupdate_graph(
            self.client, graph_id, name=name, public=public
        )

        body = validate(result)

        raw_graph = body.graphs[0]

        if raw_graph.errors is None:
            errors = None
        else:
            errors = [
                GraphErrorDetails(**error.model_dump())
                for error in raw_graph.errors
            ]

        graph = Graph(
            graph_id=raw_graph.field_id,
            name=raw_graph.name,
            workspace_id=raw_graph.field_id,
            created_at=raw_graph.created_at,
            updated_at=raw_graph.updated_at,
            schema_id=raw_graph.schema_id,
            status=raw_graph.status,
            errors=errors,
            public=raw_graph.public,
        )

        return graph

    async def export_cypher(self, graph_id: str) -> str:
        """
        Export a graph to Cypher.

        Parameters
        ----------
        graph_id : str
            The ID of the graph.

        Returns
        -------
        str
            The Cypher text.
        """
        result = await aexport_graph_cypher(self.client, graph_id)

        body = validate(result)

        return body.cypher_text

    async def query_unstructured(
        self,
        graph_id: str,
        query: str,
        return_answer: bool = True,
        include_chunks: bool = False,
    ) -> Query:
        """
        Query an unstructured graph.

        Parameters
        ----------
        graph_id : str
            The ID of the graph.
        query : str
            The query.
        return_answer : bool, optional
            Whether to return the answer.
        include_chunks : bool, optional
            Whether to include chunks.

        Returns
        -------
        Query
            The query.

        Raises
        ------
        ValueError
            If no queries are found in the response body.
        """
        result = await aquery_graph_unstructured(
            self.client,
            graph_id=graph_id,
            query=query,
            return_answer=return_answer,
            include_chunks=include_chunks,
        )

        body = validate(result)

        if body.queries is None:
            raise ValueError("No queries found in response body")

        query_raw = body.queries[0]
        nodes = [
            Node(
                node_id=raw_node.field_id,
                label=(
                    raw_node.label.root if raw_node.label is not None else ""
                ),
                name=raw_node.name,
                chunk_ids=(
                    raw_node.chunks if raw_node.chunks is not None else []
                ),
                properties=raw_node.properties,
            )
            for raw_node in (
                query_raw.nodes if query_raw.nodes is not None else []
            )
        ]

        relations_ = [
            Relation(
                name=raw_triple.relation.name,
                properties=raw_triple.relation.properties,
            )
            for raw_triple in (query_raw.triples if query_raw.triples else [])
        ]

        # nodes are uniquely determined by their ids (if id not present then name + label)
        id2node = {node.node_id: node for node in nodes}

        # relations are uniquely determined by their names
        name2relation = {relation.name: relation for relation in relations_}

        triples = [
            Triple(
                triple_id=raw_triple.field_id,
                head=id2node[raw_triple.head_node.field_id],
                tail=id2node[raw_triple.tail_node.field_id],
                relation=name2relation[raw_triple.relation.name],
                chunk_ids=raw_triple.chunks,
            )
            for raw_triple in (query_raw.triples if query_raw.triples else [])
        ]

        retval = Query(
            query_id=query_raw.field_id,
            graph_id=query_raw.graph,
            answer=(
                query_raw.response.root
                if query_raw.response is not None
                else None
            ),
            status=query_raw.status,
            created_at=query_raw.created_at,
            updated_at=query_raw.updated_at,
            nodes=nodes,
            triples=triples,
        )

        return retval

    async def get_all_triples(
        self,
        graph_id: str,
        limit: int = 10,
    ) -> AsyncIterator[Triple]:
        """
        Get all triples.

        Parameters
        ----------
        graph_id : str
            The ID of the graph.
        limit : int, optional
            The number of triples to return.

        Returns
        -------
        AsyncIterator[Triple]
            The triple iterator.

        Yields
        ------
        Triple
            The triple.
        """
        skip = 0

        while True:
            result = await aget_all_triples(
                self.client,
                graph_id=graph_id,
                skip=skip,
                limit=limit,
            )

            body = validate(result)

            if body.triples is None:
                return

            for raw_triple in body.triples:
                skip += 1

                triple = Triple(
                    triple_id=raw_triple.field_id,
                    head=Node(
                        node_id=raw_triple.head_node.field_id,
                        label=(
                            raw_triple.head_node.label.root
                            if raw_triple.head_node.label is not None
                            else ""
                        ),
                        name=raw_triple.head_node.name,
                        chunk_ids=(
                            raw_triple.head_node.chunks
                            if raw_triple.head_node.chunks is not None
                            else []
                        ),
                        properties=raw_triple.head_node.properties,
                    ),
                    tail=Node(
                        node_id=raw_triple.tail_node.field_id,
                        label=(
                            raw_triple.tail_node.label.root
                            if raw_triple.tail_node.label is not None
                            else ""
                        ),
                        name=raw_triple.tail_node.name,
                        chunk_ids=(
                            raw_triple.tail_node.chunks
                            if raw_triple.tail_node.chunks is not None
                            else []
                        ),
                        properties=raw_triple.tail_node.properties,
                    ),
                    relation=Relation(
                        name=raw_triple.relation.name,
                        properties=raw_triple.relation.properties,
                    ),
                    chunk_ids=raw_triple.chunks,
                )

                yield triple

            if len(body.triples) < limit:
                break

    async def query_structured(
        self,
        graph_id: str,
        entities: list[str] | None = None,
        relations: list[str] | None = None,
        values: list[str] | None = None,
    ) -> Query:
        """Structured query."""
        result = await aquery_graph_structured(
            self.client,
            graph_id=graph_id,
            entities=entities,
            relations=relations,
            values=values,
        )

        body = validate(result)

        if body.queries is None:
            raise ValueError("No queries found in response body")

        query_raw = body.queries[0]
        nodes = [
            Node(
                node_id=raw_node.field_id,
                label=(
                    raw_node.label.root if raw_node.label is not None else ""
                ),
                name=raw_node.name,
                chunk_ids=(
                    raw_node.chunks if raw_node.chunks is not None else []
                ),
                properties=raw_node.properties,
            )
            for raw_node in (
                query_raw.nodes if query_raw.nodes is not None else []
            )
        ]

        relations_ = [
            Relation(
                name=raw_triple.relation.name,
                properties=raw_triple.relation.properties,
            )
            for raw_triple in (query_raw.triples if query_raw.triples else [])
        ]

        # nodes are uniquely determined by their ids (if id not present then name + label)
        id2node = {node.node_id: node for node in nodes}

        # relations are uniquely determined by their names
        name2relation = {relation.name: relation for relation in relations_}

        triples = [
            Triple(
                triple_id=raw_triple.field_id,
                head=id2node[raw_triple.head_node.field_id],
                tail=id2node[raw_triple.tail_node.field_id],
                relation=name2relation[raw_triple.relation.name],
                chunk_ids=raw_triple.chunks,
            )
            for raw_triple in (query_raw.triples if query_raw.triples else [])
        ]

        retval = Query(
            query_id=query_raw.field_id,
            graph_id=query_raw.graph,
            answer=(
                query_raw.response.root
                if query_raw.response is not None
                else None
            ),
            status=query_raw.status,
            created_at=query_raw.created_at,
            updated_at=query_raw.updated_at,
            nodes=nodes,
            triples=triples,
        )

        return retval

    async def create_graph_from_triples(
        self,
        name: str,
        workspace_id: str,
        triples: list[Triple],
        schema_id: str | None = None,
    ) -> Graph:
        """
        Create a graph from triples.

        Parameters
        ----------
        name : str
            The name of the graph.
        workspace_id : str
            The ID of the workspace.
        triples : list[Triple]
            The triples.
        schema_id : str, optional
            The ID of the schema. If not provided, the schema will be inferred.

        Returns
        -------
        Graph
            The graph.
        """
        triples_raw: list[TripleRaw] = []

        for triple in triples:
            # head properties
            head_properties: dict[str, Any] = {}

            if isinstance(triple.head.properties, dict):
                head_properties.update(triple.head.properties)

            if triple.head.chunk_ids is not None:
                head_properties["chunks"] = triple.head.chunk_ids

            # tail properties
            tail_properties: dict[str, Any] = {}

            if isinstance(triple.tail.properties, dict):
                tail_properties.update(triple.tail.properties)

            if triple.tail.chunk_ids is not None:
                tail_properties["chunks"] = triple.tail.chunk_ids

            # relation properties
            relation_properties: dict[str, Any] = {}

            if isinstance(triple.relation.properties, dict):
                relation_properties.update(triple.relation.properties)

            if triple.chunk_ids is not None:
                relation_properties["chunks"] = triple.chunk_ids

            triple_raw = TripleRaw(
                head=triple.head.name,
                head_type=triple.head.label,
                relation=triple.relation.name,
                tail=triple.tail.name,
                tail_type=triple.tail.label,
                head_properties=head_properties,
                tail_properties=tail_properties,
                relation_properties=relation_properties,
            )

            triples_raw.append(triple_raw)

        request_body = CreateGraphFromTriplesRequestBody(
            name=name,
            workspace=workspace_id,
            schema=schema_id,  # type: ignore[call-arg]
            triples=triples_raw,
        )

        result = await acreate_graph_from_triples(
            self.client, body=request_body
        )

        body = validate(result)

        raw_graph = body.graphs[0]

        if raw_graph.errors is None:
            errors = None
        else:
            errors = [
                GraphErrorDetails(**error.model_dump())
                for error in raw_graph.errors
            ]

        graph = Graph(
            graph_id=raw_graph.field_id,
            name=raw_graph.name,
            workspace_id=raw_graph.workspace_id,
            created_at=raw_graph.created_at,
            updated_at=raw_graph.updated_at,
            schema_id=raw_graph.schema_id,
            status=raw_graph.status,
            errors=errors,
            public=raw_graph.public,
        )

        return graph
