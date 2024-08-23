import os
import functools
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from tolstoy_agents.utils import (
    docs_to_text,
    handle_exceptions
    )
from tolstoy_agents.retrievers.utils import _query_vectorstore


embedder = OpenAIEmbeddings(
        model = "text-embedding-ada-002",
        api_key = os.environ.get('OPENAI_API_KEY'),
    )
vectorstore = PineconeVectorStore(index_name = "toly-embeddings",
                        embedding = embedder,
                        pinecone_api_key =  os.environ.get('PINECONE_API_KEY'),
                        namespace = "fulltext",
                        text_key = "filepath")

class ToolInput(BaseModel):
    text_query: str = Field(..., description=(
        "Text quesition which will be embedded and compared to our codebase."
        )
    )

@handle_exceptions
def product_documentation(text_query: str,
                          repo_path: str,
                          chunk_size: int,
                           ) -> str:
    relevant_docs = _query_vectorstore(
                            repo_path,
                            chunk_size,
                            vectorstore,
                            text_query)

    res = docs_to_text(relevant_docs)

    return res


def relevant_documents(text_query: str,
                          repo_path: str,
                          chunk_size: int,
                           ) -> str:
    relevant_docs = _query_vectorstore(
                            repo_path,
                            chunk_size,
                            vectorstore,
                            text_query)

    return relevant_docs


def relevant_documents_factory(
                          repo_path: str,
                          chunk_size: int,
                           ) -> str:
    return functools.partial(
            relevant_documents,
            repo_path=repo_path,
            chunk_size=chunk_size
        )


def product_documentation_factory(
                            repo_path,
                            chunk_size) -> StructuredTool:
    return StructuredTool.from_function(
        func=functools.partial(
            product_documentation,
            repo_path=repo_path,
            chunk_size=chunk_size,
        ),
        name="product_documentation",
        description= (
            "Some documentation about the Tolstoy product we are building"
        ),
        args_schema=ToolInput,
        return_direct=False
    )
