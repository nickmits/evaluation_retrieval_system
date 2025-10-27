"""
Retrieval Systems
Abstract base classes and implementations for different RAG retrieval strategies
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langchain_community.retrievers import BM25Retriever
from langchain.chat_models import init_chat_model
import time


class BaseRetrievalSystem(ABC):
    """Abstract base class for all retrieval systems"""

    def __init__(
        self,
        document_path: str,
        openai_api_key: str,
        cohere_api_key: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.document_path = document_path
        self.openai_api_key = openai_api_key
        self.cohere_api_key = cohere_api_key
        self.config = config or {}
        self.retriever = None
        self.chunks = []
        self.initialization_time = 0

    @abstractmethod
    def initialize(self) -> 'BaseRetrievalSystem':
        """Initialize the retrieval system"""
        pass

    @abstractmethod
    def get_system_name(self) -> str:
        """Get the name of the retrieval system"""
        pass

    @abstractmethod
    def get_system_description(self) -> str:
        """Get a description of the retrieval system"""
        pass

    def search(self, query: str, k: int = 10) -> List[Document]:
        """Search for relevant documents"""
        if not self.retriever:
            raise ValueError("Call initialize() first")
        return self.retriever.get_relevant_documents(query)[:k]

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary metrics about the system"""
        return {
            "system_name": self.get_system_name(),
            "num_chunks": len(self.chunks),
            "initialization_time": self.initialization_time,
            "config": self.config
        }


class SimpleRecursiveRetrieval(BaseRetrievalSystem):
    """Simple retrieval with RecursiveCharacterTextSplitter"""

    def get_system_name(self) -> str:
        return "Simple Recursive Chunking"

    def get_system_description(self) -> str:
        return "Baseline system using RecursiveCharacterTextSplitter + Vector Search"

    def initialize(self) -> 'SimpleRecursiveRetrieval':
        start_time = time.time()

        chunk_size = self.config.get('chunk_size', 1000)
        chunk_overlap = self.config.get('chunk_overlap', 200)

        print(f"[INIT] {self.get_system_name()}")
        print(f"  - Chunk size: {chunk_size}")
        print(f"  - Chunk overlap: {chunk_overlap}")

        # Load documents
        loader = PyMuPDFLoader(self.document_path)
        pages = loader.load()

        # Add metadata
        for i, page in enumerate(pages):
            page.metadata.update({
                "page_number": i + 1,
                "source_type": "pdf_fulltext"
            })

        # Chunk with RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.chunks = text_splitter.split_documents(pages)

        print(f"  - Created {len(self.chunks)} chunks")

        # Create vector store
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=self.openai_api_key
        )

        vectorstore = Qdrant.from_documents(
            self.chunks,
            embeddings,
            location=":memory:",
            collection_name="simple_recursive"
        )

        self.retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

        self.initialization_time = time.time() - start_time
        print(f"  - Initialization time: {self.initialization_time:.2f}s")

        return self


class SimpleSemanticRetrieval(BaseRetrievalSystem):
    """Simple retrieval with SemanticChunker"""

    def get_system_name(self) -> str:
        return "Simple Semantic Chunking"

    def get_system_description(self) -> str:
        return "SemanticChunker + Vector Search (context-aware splitting)"

    def initialize(self) -> 'SimpleSemanticRetrieval':
        start_time = time.time()

        threshold_type = self.config.get('threshold_type', 'percentile')
        threshold_amount = self.config.get('threshold_amount', 95)

        print(f"[INIT] {self.get_system_name()}")
        print(f"  - Threshold type: {threshold_type}")
        print(f"  - Threshold amount: {threshold_amount}")

        # Load documents
        loader = PyMuPDFLoader(self.document_path)
        pages = loader.load()

        # Add metadata
        for i, page in enumerate(pages):
            page.metadata.update({
                "page_number": i + 1,
                "source_type": "pdf_fulltext"
            })

        # Create embeddings model
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=self.openai_api_key
        )

        # Chunk with SemanticChunker
        text_splitter = SemanticChunker(
            embeddings,
            breakpoint_threshold_type=threshold_type,
            breakpoint_threshold_amount=threshold_amount
        )
        self.chunks = text_splitter.split_documents(pages)

        print(f"  - Created {len(self.chunks)} semantic chunks")

        # Create vector store
        vectorstore = Qdrant.from_documents(
            self.chunks,
            embeddings,
            location=":memory:",
            collection_name="simple_semantic"
        )

        self.retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

        self.initialization_time = time.time() - start_time
        print(f"  - Initialization time: {self.initialization_time:.2f}s")

        return self


class AdvancedRecursiveRetrieval(BaseRetrievalSystem):
    """Advanced ensemble retrieval with RecursiveCharacterTextSplitter"""

    def get_system_name(self) -> str:
        return "Advanced Recursive (Ensemble)"

    def get_system_description(self) -> str:
        return "Recursive chunking + BM25 + Multi-Query + Cohere Reranking"

    def initialize(self) -> 'AdvancedRecursiveRetrieval':
        start_time = time.time()

        chunk_size = self.config.get('chunk_size', 1000)
        chunk_overlap = self.config.get('chunk_overlap', 200)

        print(f"[INIT] {self.get_system_name()}")
        print(f"  - Chunk size: {chunk_size}")
        print(f"  - Chunk overlap: {chunk_overlap}")

        # Load documents
        loader = PyMuPDFLoader(self.document_path)
        pages = loader.load()

        # Add metadata
        for i, page in enumerate(pages):
            page.metadata.update({
                "page_number": i + 1,
                "source_type": "pdf_fulltext"
            })

        # Chunk with RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.chunks = text_splitter.split_documents(pages)

        print(f"  - Created {len(self.chunks)} chunks")

        # Initialize models
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=self.openai_api_key
        )

        chat_model = init_chat_model(
            model="openai:gpt-4o-mini",
            api_key=self.openai_api_key,
            temperature=0.1
        )

        # Create vector store
        vectorstore = Qdrant.from_documents(
            self.chunks,
            embeddings,
            location=":memory:",
            collection_name="advanced_recursive"
        )

        # Build ensemble retriever
        print("  - Building ensemble retriever...")

        # 1. BM25 Retriever
        bm25_retriever = BM25Retriever.from_documents(self.chunks)
        bm25_retriever.k = 10

        # 2. Multi-Query Retriever
        multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=vectorstore.as_retriever(search_kwargs={"k": 15}),
            llm=chat_model
        )

        # 3. Optional Cohere Reranking
        if self.cohere_api_key:
            print("  - Using Cohere reranking")
            compression_retriever = ContextualCompressionRetriever(
                base_retriever=multi_query_retriever,
                base_compressor=CohereRerank(
                    model="rerank-v3.5",
                    cohere_api_key=self.cohere_api_key
                )
            )
            self.retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, multi_query_retriever, compression_retriever],
                weights=[0.3, 0.3, 0.4]
            )
        else:
            print("  - No Cohere key, using BM25 + Multi-Query only")
            self.retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, multi_query_retriever],
                weights=[0.5, 0.5]
            )

        self.initialization_time = time.time() - start_time
        print(f"  - Initialization time: {self.initialization_time:.2f}s")

        return self


class AdvancedSemanticRetrieval(BaseRetrievalSystem):
    """Advanced ensemble retrieval with SemanticChunker"""

    def get_system_name(self) -> str:
        return "Advanced Semantic (Ensemble)"

    def get_system_description(self) -> str:
        return "Semantic chunking + BM25 + Multi-Query + Cohere Reranking"

    def initialize(self) -> 'AdvancedSemanticRetrieval':
        start_time = time.time()

        threshold_type = self.config.get('threshold_type', 'percentile')
        threshold_amount = self.config.get('threshold_amount', 95)

        print(f"[INIT] {self.get_system_name()}")
        print(f"  - Threshold type: {threshold_type}")
        print(f"  - Threshold amount: {threshold_amount}")

        # Load documents
        loader = PyMuPDFLoader(self.document_path)
        pages = loader.load()

        # Add metadata
        for i, page in enumerate(pages):
            page.metadata.update({
                "page_number": i + 1,
                "source_type": "pdf_fulltext"
            })

        # Initialize models
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=self.openai_api_key
        )

        chat_model = init_chat_model(
            model="openai:gpt-4o-mini",
            api_key=self.openai_api_key,
            temperature=0.1
        )

        # Chunk with SemanticChunker
        text_splitter = SemanticChunker(
            embeddings,
            breakpoint_threshold_type=threshold_type,
            breakpoint_threshold_amount=threshold_amount
        )
        self.chunks = text_splitter.split_documents(pages)

        print(f"  - Created {len(self.chunks)} semantic chunks")

        # Create vector store
        vectorstore = Qdrant.from_documents(
            self.chunks,
            embeddings,
            location=":memory:",
            collection_name="advanced_semantic"
        )

        # Build ensemble retriever
        print("  - Building ensemble retriever...")

        # 1. BM25 Retriever
        bm25_retriever = BM25Retriever.from_documents(self.chunks)
        bm25_retriever.k = 10

        # 2. Multi-Query Retriever
        multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=vectorstore.as_retriever(search_kwargs={"k": 15}),
            llm=chat_model
        )

        # 3. Optional Cohere Reranking
        if self.cohere_api_key:
            print("  - Using Cohere reranking")
            compression_retriever = ContextualCompressionRetriever(
                base_retriever=multi_query_retriever,
                base_compressor=CohereRerank(
                    model="rerank-v3.5",
                    cohere_api_key=self.cohere_api_key
                )
            )
            self.retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, multi_query_retriever, compression_retriever],
                weights=[0.3, 0.3, 0.4]
            )
        else:
            print("  - No Cohere key, using BM25 + Multi-Query only")
            self.retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, multi_query_retriever],
                weights=[0.5, 0.5]
            )

        self.initialization_time = time.time() - start_time
        print(f"  - Initialization time: {self.initialization_time:.2f}s")

        return self


class RetrievalSystemFactory:
    """Factory for creating retrieval systems"""

    SYSTEMS = {
        "simple_recursive": SimpleRecursiveRetrieval,
        "simple_semantic": SimpleSemanticRetrieval,
        "advanced_recursive": AdvancedRecursiveRetrieval,
        "advanced_semantic": AdvancedSemanticRetrieval
    }

    @classmethod
    def create_system(
        cls,
        system_type: str,
        document_path: str,
        openai_api_key: str,
        cohere_api_key: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> BaseRetrievalSystem:
        """Create a retrieval system by type"""

        if system_type not in cls.SYSTEMS:
            available = ", ".join(cls.SYSTEMS.keys())
            raise ValueError(f"Unknown system type: {system_type}. Available: {available}")

        system_class = cls.SYSTEMS[system_type]
        return system_class(
            document_path=document_path,
            openai_api_key=openai_api_key,
            cohere_api_key=cohere_api_key,
            config=config
        )

    @classmethod
    def get_available_systems(cls) -> List[str]:
        """Get list of available system types"""
        return list(cls.SYSTEMS.keys())
