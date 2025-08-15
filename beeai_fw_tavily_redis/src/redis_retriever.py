#!/usr/bin/env python

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from beeai_framework.tools import ToolOutput, tool
from beeai_framework.utils.strings import to_json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore
from pydantic import BaseModel, Field

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================
# Configuration settings and environment variables

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# =============================================================================
# VECTOR STORE AND EMBEDDINGS SETUP
# =============================================================================
# Core class that manages the embedding model and Redis vector database connection
class RAGRetriever:

    def __init__(self):

        model_name = "sentence-transformers/all-mpnet-base-v2"  # or "openai:o4-mini-2025-04-16"
        print(f"RAG retriever using {model_name} for embeddings.")
        embeddings = HuggingFaceEmbeddings(model_name=model_name)

        # Configure and init the vector store with our embeddings model
        index_name = "internal_docs"
        print(f"RAG retriever using {index_name} Redis vector store index name.")
        config = RedisConfig(
            index_name=index_name,
            redis_url=REDIS_URL,
            metadata_schema=[
                {"name": "document", "type": "tag"},
            ],
        )

        self.vector_store = RedisVectorStore(embeddings, config=config)

# =============================================================================
# INPUT/OUTPUT DATA MODELS
# =============================================================================
# Pydantic models that define the structure and validation for tool inputs and outputs.
# Important for compatibility with LLMs like those from OpenAI.

class DocSearchInput(BaseModel):
    query: str = Field(..., description="The query to search for in company internal documents.")

# Data model for individual search results with content, metadata, and similarity score
class RagToolResult(BaseModel):
    content: str
    metadata: dict
    score: float

# Custom output class that extends framework's ToolOutput for RAG-specific results
class RagToolOutput(ToolOutput):
    def __init__(self, results: list[RagToolResult]) -> None:
        super().__init__()
        self.results = results

    def get_text_content(self) -> str:
        return to_json(self.results)

    def is_empty(self) -> bool:
        return len(self.results) == 0

# =============================================================================
# MAIN RAG TOOL IMPLEMENTATION
# =============================================================================
# The core tool function that performs semantic search and returns relevant document sections

# Use the input_schema argument to tell the @tool decorator to expect structured input.
# The function now takes a single argument of type str.
# The function result format uses the RagToolOutput schema.

# Using the BeeAI framework there are two ways to create a custom tool. 
# You can extend the base tool class (like the Tavily Tool does) or you can use a tool decorator with your required inputs
# [INSERT YOUR CODE HERE]
def internal_document_search(query: str) -> RagToolOutput:
    """Tool that answers a query about company policy using company internal documents. Returns up to top_n results below the similarity distance threshold."""
    retriever = RAGRetriever()
    print("Searching vector store...")
    results = retriever.vector_store.similarity_search_with_score(
        query, k=4, distance_threshold=0.6
    )
    output = []
    # Format the results for output
    for doc, score in results:
        output.append(RagToolResult(
            content=getattr(doc, "page_content", str(doc)),
            metadata=getattr(doc, "metadata", {}),
            score=score
        ))

    print(f"Vector store search returned {len(output)} top results.")
    return RagToolOutput(output)

# =============================================================================
# TESTING AND DEMONSTRATION
# =============================================================================
# Test code to verify the RAG tool works correctly with sample queries

if __name__ == "__main__":

    rag_retriever = RAGRetriever()

    question = "What is our target market for the pilot?"
    print("QUESTION: ", question)

    answer = rag_retriever.vector_store.similarity_search_with_score(question)
    print("ANSWER:")
    for doc, score in answer:
        print(f"Score: {score:.3f}")
        print(f"Content: {getattr(doc, 'page_content', str(doc))[:500]}") # print only 500 characters
        print(f"Metadata: {getattr(doc, 'metadata', {})}")
        print()
