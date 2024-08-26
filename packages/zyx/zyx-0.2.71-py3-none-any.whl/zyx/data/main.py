from sqlmodel import Field, Session, SQLModel, create_engine, select
from ..core.ext import BaseModel
from typing import List, Optional, Union, Callable, Literal
import uuid
from .. import logger


class SQLModelNode(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    text: str
    embedding: List[float]
    metadata: Optional[dict] = Field(default=None)


class SearchResponse(BaseModel):
    query: str
    results: List[SQLModelNode] = Field(default_factory=list)


class SQLModelVectorDB:
    def __init__(
        self,
        database_url: str = "sqlite:///:memory:",
        embedding_model: str = "text-embedding-3-small",
        embedding_dimensions: Optional[int] = None,
        embedding_api_key: Optional[str] = None,
        embedding_api_base: Optional[str] = None,
        embedding_api_version: Optional[str] = None,
    ):
        self.engine = create_engine(database_url)
        SQLModel.metadata.create_all(self.engine)
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.embedding_api_key = embedding_api_key
        self.embedding_api_base = embedding_api_base
        self.embedding_api_version = embedding_api_version

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
        if isinstance(texts, str):
            texts = [texts]

        with Session(self.engine) as session:
            for text in texts:
                try:
                    embedding_vector = self._get_embedding(text)
                    node = SQLModelNode(
                        text=text, embedding=embedding_vector, metadata=metadata or {}
                    )
                    session.add(node)
                except Exception as e:
                    logger.error(f"Error processing text: {text}. Error: {e}")
            session.commit()

    def search(self, query: str, top_k: int = 5) -> SearchResponse:
        try:
            query_vector = self._get_embedding(query)

            with Session(self.engine) as session:
                # This is a simple cosine similarity calculation
                statement = (
                    select(SQLModelNode)
                    .order_by(
                        sum(
                            SQLModelNode.embedding[i] * query_vector[i]
                            for i in range(len(query_vector))
                        ).desc()
                    )
                    .limit(top_k)
                )

                results = session.exec(statement).all()

                return SearchResponse(query=query, results=results)
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
        mode: Optional[Literal["tools"]] = "tools",
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
        db = SQLModelVectorDB()
        db.add(["Hello, world!", "How are you?", "What's up?"])
        results = db.search("How are you?")
        for result in results.results:
            print(f"ID: {result.id}, Text: {result.text}, Metadata: {result.metadata}")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
