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
from langchain_cohere import CohereEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.retrievers import EnsembleRetriever, ParentDocumentRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langchain_community.retrievers import BM25Retriever
from langchain.chat_models import init_chat_model
from langchain.storage import InMemoryStore
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

        # Extract sub-configs
        self.embedding_config = self.config.get('embedding_config', {
            'provider': 'openai',
            'model': 'text-embedding-3-small',
            'dimensions': None
        })
        self.retrieval_config = self.config.get('retrieval_config', {
            'base_k': 10,
            'bm25_k': 10,
            'multi_query_k': 15,
            'final_k': 10
        })
        self.ensemble_weights = self.config.get('ensemble_weights', {
            'bm25_weight': 0.3,
            'vector_weight': 0.3,
            'multi_query_weight': 0.2,
            'reranking_weight': 0.2
        })

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

    def create_embeddings(self):
        """Create embeddings based on configuration"""
        provider = self.embedding_config.get('provider', 'openai')
        model = self.embedding_config.get('model', 'text-embedding-3-small')

        if provider == 'openai':
            return OpenAIEmbeddings(
                model=model,
                api_key=self.openai_api_key
            )
        elif provider == 'cohere':
            if not self.cohere_api_key:
                raise ValueError("Cohere API key required for Cohere embeddings")
            return CohereEmbeddings(
                model=model,
                cohere_api_key=self.cohere_api_key
            )
        elif provider == 'huggingface':
            return HuggingFaceEmbeddings(
                model_name=model
            )
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")

    def search(self, query: str, k: int = 10) -> List[Document]:
        """Search for relevant documents"""
        if not self.retriever:
            raise ValueError("Call initialize() first")
        # Use configured final_k
        final_k = self.retrieval_config.get('final_k', k)
        return self.retriever.get_relevant_documents(query)[:final_k]

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

        # Create vector store with configured embeddings
        embeddings = self.create_embeddings()
        print(f"  - Using embeddings: {self.embedding_config.get('provider')}:{self.embedding_config.get('model')}")

        vectorstore = Qdrant.from_documents(
            self.chunks,
            embeddings,
            location=":memory:",
            collection_name="simple_recursive"
        )

        # Use configured retrieval k
        base_k = self.retrieval_config.get('base_k', 10)
        print(f"  - Retrieval top-k: {base_k}")

        self.retriever = vectorstore.as_retriever(search_kwargs={"k": base_k})

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

        # Create embeddings model with configuration
        embeddings = self.create_embeddings()
        print(f"  - Using embeddings: {self.embedding_config.get('provider')}:{self.embedding_config.get('model')}")

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

        # Use configured retrieval k
        base_k = self.retrieval_config.get('base_k', 10)
        print(f"  - Retrieval top-k: {base_k}")

        self.retriever = vectorstore.as_retriever(search_kwargs={"k": base_k})

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

        # Initialize models with configured embeddings
        embeddings = self.create_embeddings()
        print(f"  - Using embeddings: {self.embedding_config.get('provider')}:{self.embedding_config.get('model')}")

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

        # Get configured k values
        base_k = self.retrieval_config.get('base_k', 10)
        bm25_k = self.retrieval_config.get('bm25_k', 10)
        multi_query_k = self.retrieval_config.get('multi_query_k', 15)
        print(f"  - Retrieval config: base_k={base_k}, bm25_k={bm25_k}, multi_query_k={multi_query_k}")

        # Build ensemble retriever
        print("  - Building ensemble retriever...")

        # 1. BM25 Retriever with configured k
        bm25_retriever = BM25Retriever.from_documents(self.chunks)
        bm25_retriever.k = bm25_k

        # 2. Multi-Query Retriever with configured k
        multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=vectorstore.as_retriever(search_kwargs={"k": multi_query_k}),
            llm=chat_model
        )

        # Get configured weights
        bm25_weight = self.ensemble_weights.get('bm25_weight', 0.3)
        multi_query_weight = self.ensemble_weights.get('multi_query_weight', 0.3)
        reranking_weight = self.ensemble_weights.get('reranking_weight', 0.4)

        # 3. Optional Cohere Reranking
        if self.cohere_api_key:
            print(f"  - Using Cohere reranking with weights: [{bm25_weight}, {multi_query_weight}, {reranking_weight}]")
            compression_retriever = ContextualCompressionRetriever(
                base_retriever=multi_query_retriever,
                base_compressor=CohereRerank(
                    model="rerank-v3.5",
                    cohere_api_key=self.cohere_api_key
                )
            )
            self.retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, multi_query_retriever, compression_retriever],
                weights=[bm25_weight, multi_query_weight, reranking_weight]
            )
        else:
            # Normalize weights without reranking
            total = bm25_weight + multi_query_weight
            w1 = bm25_weight / total
            w2 = multi_query_weight / total
            print(f"  - No Cohere key, using BM25 + Multi-Query with weights: [{w1:.2f}, {w2:.2f}]")
            self.retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, multi_query_retriever],
                weights=[w1, w2]
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

        # Initialize models with configured embeddings
        embeddings = self.create_embeddings()
        print(f"  - Using embeddings: {self.embedding_config.get('provider')}:{self.embedding_config.get('model')}")

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

        # Get configured k values
        base_k = self.retrieval_config.get('base_k', 10)
        bm25_k = self.retrieval_config.get('bm25_k', 10)
        multi_query_k = self.retrieval_config.get('multi_query_k', 15)
        print(f"  - Retrieval config: base_k={base_k}, bm25_k={bm25_k}, multi_query_k={multi_query_k}")

        # Build ensemble retriever
        print("  - Building ensemble retriever...")

        # 1. BM25 Retriever with configured k
        bm25_retriever = BM25Retriever.from_documents(self.chunks)
        bm25_retriever.k = bm25_k

        # 2. Multi-Query Retriever with configured k
        multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=vectorstore.as_retriever(search_kwargs={"k": multi_query_k}),
            llm=chat_model
        )

        # Get configured weights
        bm25_weight = self.ensemble_weights.get('bm25_weight', 0.3)
        multi_query_weight = self.ensemble_weights.get('multi_query_weight', 0.3)
        reranking_weight = self.ensemble_weights.get('reranking_weight', 0.4)

        # 3. Optional Cohere Reranking
        if self.cohere_api_key:
            print(f"  - Using Cohere reranking with weights: [{bm25_weight}, {multi_query_weight}, {reranking_weight}]")
            compression_retriever = ContextualCompressionRetriever(
                base_retriever=multi_query_retriever,
                base_compressor=CohereRerank(
                    model="rerank-v3.5",
                    cohere_api_key=self.cohere_api_key
                )
            )
            self.retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, multi_query_retriever, compression_retriever],
                weights=[bm25_weight, multi_query_weight, reranking_weight]
            )
        else:
            # Normalize weights without reranking
            total = bm25_weight + multi_query_weight
            w1 = bm25_weight / total
            w2 = multi_query_weight / total
            print(f"  - No Cohere key, using BM25 + Multi-Query with weights: [{w1:.2f}, {w2:.2f}]")
            self.retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, multi_query_retriever],
                weights=[w1, w2]
            )

        self.initialization_time = time.time() - start_time
        print(f"  - Initialization time: {self.initialization_time:.2f}s")

        return self


class ParentDocumentRetrieval(BaseRetrievalSystem):
    """Parent Document Retrieval - searches small chunks but retrieves full parent documents"""

    def get_system_name(self) -> str:
        return "Parent Document Retrieval"

    def get_system_description(self) -> str:
        return "Stores small chunks for search, retrieves larger parent documents for context"

    def initialize(self) -> 'ParentDocumentRetrieval':
        start_time = time.time()

        # Config for parent chunks (larger chunks or full documents)
        parent_chunk_size = self.config.get('parent_chunk_size', 2000)
        parent_chunk_overlap = self.config.get('parent_chunk_overlap', 200)

        # Config for child chunks (smaller chunks for embedding)
        child_chunk_size = self.config.get('child_chunk_size', 400)
        child_chunk_overlap = self.config.get('child_chunk_overlap', 50)

        print(f"[INIT] {self.get_system_name()}")
        print(f"  - Parent chunk size: {parent_chunk_size}")
        print(f"  - Child chunk size: {child_chunk_size}")

        # Load documents
        loader = PyMuPDFLoader(self.document_path)
        pages = loader.load()

        # Add metadata
        for i, page in enumerate(pages):
            page.metadata.update({
                "page_number": i + 1,
                "source_type": "pdf_fulltext"
            })

        # Initialize embeddings with configuration
        embeddings = self.create_embeddings()
        print(f"  - Using embeddings: {self.embedding_config.get('provider')}:{self.embedding_config.get('model')}")

        # Create splitters first
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=parent_chunk_overlap
        )

        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=child_chunk_overlap
        )

        # Split documents into parent chunks first
        parent_docs = parent_splitter.split_documents(pages)

        # Create vector store by initializing with a dummy text to set embedding dimension
        # This is needed because Qdrant needs to know the embedding size
        child_vectorstore = Qdrant.from_texts(
            texts=["init"],  # Dummy text to initialize
            embedding=embeddings,
            location=":memory:",
            collection_name="parent_doc_children"
        )

        # Create document store for parent documents (what we return)
        parent_docstore = InMemoryStore()

        # Create ParentDocumentRetriever
        self.retriever = ParentDocumentRetriever(
            vectorstore=child_vectorstore,
            docstore=parent_docstore,
            child_splitter=child_splitter,
        )

        # Add documents to the retriever (it will handle splitting and storing)
        self.retriever.add_documents(parent_docs, ids=None)

        # Store chunks for metrics (count child chunks)
        self.chunks = child_splitter.split_documents(
            parent_splitter.split_documents(pages)
        )

        print(f"  - Created {len(self.chunks)} child chunks")
        print(f"  - Parent documents stored in docstore")

        self.initialization_time = time.time() - start_time
        print(f"  - Initialization time: {self.initialization_time:.2f}s")

        return self


class AdvancedParentDocumentRetrieval(BaseRetrievalSystem):
    """Advanced ensemble retrieval with ParentDocumentRetriever"""

    def get_system_name(self) -> str:
        return "Advanced Parent Document (Ensemble)"

    def get_system_description(self) -> str:
        return "Parent Document + BM25 + Multi-Query + Cohere Reranking"

    def initialize(self) -> 'AdvancedParentDocumentRetrieval':
        start_time = time.time()

        # Config for parent chunks (larger chunks or full documents)
        parent_chunk_size = self.config.get('parent_chunk_size', 2000)
        parent_chunk_overlap = self.config.get('parent_chunk_overlap', 200)

        # Config for child chunks (smaller chunks for embedding)
        child_chunk_size = self.config.get('child_chunk_size', 400)
        child_chunk_overlap = self.config.get('child_chunk_overlap', 50)

        print(f"[INIT] {self.get_system_name()}")
        print(f"  - Parent chunk size: {parent_chunk_size}")
        print(f"  - Child chunk size: {child_chunk_size}")

        # Load documents
        loader = PyMuPDFLoader(self.document_path)
        pages = loader.load()

        # Add metadata
        for i, page in enumerate(pages):
            page.metadata.update({
                "page_number": i + 1,
                "source_type": "pdf_fulltext"
            })

        # Initialize embeddings with configuration
        embeddings = self.create_embeddings()
        print(f"  - Using embeddings: {self.embedding_config.get('provider')}:{self.embedding_config.get('model')}")

        # Initialize chat model for multi-query
        chat_model = init_chat_model(
            model="openai:gpt-4o-mini",
            api_key=self.openai_api_key,
            temperature=0.1
        )

        # Create splitters
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=parent_chunk_overlap
        )

        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=child_chunk_overlap
        )

        # Split documents into parent chunks
        parent_docs = parent_splitter.split_documents(pages)

        # Store all chunks for metrics and BM25
        self.chunks = child_splitter.split_documents(parent_docs)

        print(f"  - Created {len(self.chunks)} child chunks from {len(parent_docs)} parent chunks")

        # Create vector store for child chunks
        child_vectorstore = Qdrant.from_texts(
            texts=["init"],  # Dummy text to initialize
            embedding=embeddings,
            location=":memory:",
            collection_name="advanced_parent_doc_children"
        )

        # Create document store for parent documents
        parent_docstore = InMemoryStore()

        # Create ParentDocumentRetriever
        parent_doc_retriever = ParentDocumentRetriever(
            vectorstore=child_vectorstore,
            docstore=parent_docstore,
            child_splitter=child_splitter,
        )

        # Add documents to the retriever
        parent_doc_retriever.add_documents(parent_docs, ids=None)

        # Get configured k values
        bm25_k = self.retrieval_config.get('bm25_k', 10)
        print(f"  - Retrieval config: bm25_k={bm25_k}")

        # Build ensemble retriever
        print("  - Building ensemble retriever...")

        # 1. BM25 Retriever (on parent chunks for consistency) with configured k
        bm25_retriever = BM25Retriever.from_documents(parent_docs)
        bm25_retriever.k = bm25_k

        # 2. Multi-Query Retriever (wraps parent doc retriever)
        multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=parent_doc_retriever,
            llm=chat_model
        )

        # Get configured weights
        bm25_weight = self.ensemble_weights.get('bm25_weight', 0.25)
        vector_weight = self.ensemble_weights.get('vector_weight', 0.25)
        multi_query_weight = self.ensemble_weights.get('multi_query_weight', 0.25)
        reranking_weight = self.ensemble_weights.get('reranking_weight', 0.25)

        # 3. Optional Cohere Reranking
        if self.cohere_api_key:
            print(f"  - Using Cohere reranking with weights: [{bm25_weight}, {vector_weight}, {multi_query_weight}, {reranking_weight}]")
            compression_retriever = ContextualCompressionRetriever(
                base_retriever=multi_query_retriever,
                base_compressor=CohereRerank(
                    model="rerank-v3.5",
                    cohere_api_key=self.cohere_api_key
                )
            )
            self.retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, parent_doc_retriever, multi_query_retriever, compression_retriever],
                weights=[bm25_weight, vector_weight, multi_query_weight, reranking_weight]
            )
        else:
            # Normalize weights without reranking (3-way ensemble)
            total = bm25_weight + vector_weight + multi_query_weight
            w1 = bm25_weight / total
            w2 = vector_weight / total
            w3 = multi_query_weight / total
            print(f"  - No Cohere key, using BM25 + ParentDoc + Multi-Query with weights: [{w1:.2f}, {w2:.2f}, {w3:.2f}]")
            self.retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, parent_doc_retriever, multi_query_retriever],
                weights=[w1, w2, w3]
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
        "advanced_semantic": AdvancedSemanticRetrieval,
        "parent_document": ParentDocumentRetrieval,
        "advanced_parent_document": AdvancedParentDocumentRetrieval
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
