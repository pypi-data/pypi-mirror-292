from qdrant_client.http import models as rest
from pydantic import BaseModel, Field
from typing import Callable, List, Union, Optional, Literal
import uuid
import logging

from ..types import ClientModeParams, ClientParams
from .. import logger


class QdrantNode(BaseModel):
    id: str
    text: str
    embedding: List[float]
    metadata: Optional[dict] = None


class SearchResponse(BaseModel):
    query: str
    results: List[QdrantNode] = Field(default_factory=list)


class Qdrant:
    def __init__(
        self,
        collection_name: str = "my_collection",
        vector_size: int = 1536,
        distance: Literal["Cosine", "Euclid", "Dot"] = "Cosine",
        location: str = ":memory:",
        host: str = None,
        port: int = 6333,
        embedding_model: str = "text-embedding-3-small",
        embedding_dimensions: Optional[int] = None,
        embedding_api_key: Optional[str] = None,
        embedding_api_base: Optional[str] = None,
        embedding_api_version: Optional[str] = None,
    ):
        from qdrant_client.http.models import Distance
        from qdrant_client import QdrantClient

        self.client = QdrantClient(location=location, host=host, port=port)
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = Distance(distance)
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.embedding_api_key = embedding_api_key
        self.embedding_api_base = embedding_api_base
        self.embedding_api_version = embedding_api_version

        self._create_collection()

    def _create_collection(self):
        from qdrant_client.http.models import VectorParams

        try:
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists.")
        except Exception as e:
            logger.info(
                f"Collection '{self.collection_name}' does not exist. Creating it now."
            )
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size, distance=self.distance
                ),
            )
            logger.info(f"Collection '{self.collection_name}' created successfully.")

    def _get_embedding(self, text: str) -> List[float]:
        from litellm.main import embedding as litellm_embedding

        try:
            response = litellm_embedding(
                model=self.embedding_model,
                input=[text],
                dimensions=self.embedding_dimensions,
                api_key=self.embedding_api_key,
                api_base=self.embedding_api_base,
                api_version=self.embedding_api_version,
            )

            embedding_data = response.get("data", None)
            if (
                embedding_data
                and isinstance(embedding_data, list)
                and len(embedding_data) > 0
            ):
                embedding_vector = embedding_data[0].get("embedding", None)
                if isinstance(embedding_vector, list) and all(
                    isinstance(x, float) for x in embedding_vector
                ):
                    return embedding_vector
                else:
                    raise ValueError(
                        "Invalid embedding format: Expected a list of floats within the 'embedding' key"
                    )
            else:
                raise ValueError("Embedding data is missing or improperly formatted")
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def add(self, texts: Union[str, List[str]], metadata: Optional[dict] = None):
        from qdrant_client.http.models import PointStruct

        if isinstance(texts, str):
            texts = [texts]

        points = []
        for text in texts:
            try:
                embedding_vector = self._get_embedding(text)
                node_id = str(uuid.uuid4())
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding_vector,
                    payload={"text": text, "metadata": metadata or {}},
                )
                points.append(point)
            except Exception as e:
                logger.error(f"Error processing text: {text}. Error: {e}")

        if points:
            try:
                self.client.upsert(collection_name=self.collection_name, points=[point])
                logger.info(
                    f"Successfully added {len(points)} points to the collection."
                )
            except Exception as e:
                logger.error(f"Error upserting points to collection: {e}")
        else:
            logger.warning("No valid points to add to the collection.")

    def search(self, query: str, top_k: int = 5) -> SearchResponse:
        try:
            query_vector = self._get_embedding(query)
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
            )

            nodes = []
            for result in search_results:
                payload = result.payload
                node = QdrantNode(
                    id=str(result.id),
                    text=payload.get("text", ""),
                    embedding=query_vector,
                    metadata=payload.get("metadata", {}),
                )
                nodes.append(node)
            return SearchResponse(query=query, results=nodes)
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise

    def completion(
        self,
        messages: Union[str, list[dict[str, str]]],
        model: Optional[str] = "gpt-4o-mini",
        top_k: Optional[int] = 5,
        tools: Optional[List[Union[Callable, dict, BaseModel]]] = None,
        run_tools: Optional[bool] = True,
        response_model: Optional[BaseModel] = None,
        mode: Optional[ClientModeParams] = "tools",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        top_p: Optional[float] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_retries: Optional[int] = 3,
        verbose: Optional[bool] = False,
    ):
        if isinstance(messages, str):
            query = messages
            messages = [{"role": "user", "content": messages}]
        elif isinstance(messages, list):
            query = messages[-1].get("content", "")

        try:
            results = self.search(query, top_k=top_k)
        except Exception as e:
            logger.error(f"Error during search: {e}")
            results = SearchResponse(query=query)

        if messages and isinstance(messages, list):
            if not any(message.get("role", "") == "system" for message in messages):
                messages.insert(
                    0,
                    {
                        "role": "system",
                        "content": f"You have retrieved the following relevant information. Use only if relevant {results}",
                    },
                )
            else:
                for message in messages:
                    if message.get("role", "") == "system":
                        message["content"] += (
                            f" You have retrieved the following relevant information. Use only if relevant {results}"
                        )
                        break
        from ..client.main import Client

        return Client().completion(
            messages=messages,
            model=model,
            tools=tools,
            run_tools=run_tools,
            response_model=response_model,
            mode=mode,
            base_url=base_url,
            api_key=api_key,
            organization=organization,
            top_p=top_p,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            verbose=verbose,
        )


if __name__ == "__main__":
    try:
        qdrant = Qdrant(collection_name="my_collection", vector_size=1536)
        qdrant.add(["Hello, world!", "How are you?", "What's up?"])
        results = qdrant.search("How are you?")
        for result in results.results:
            print(f"ID: {result.id}, Text: {result.text}, Metadata: {result.metadata}")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
