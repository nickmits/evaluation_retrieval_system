"""
Document Processor
Handles document upload, processing, and preparation for RAG evaluation
"""

from typing import List, Optional
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_core.documents import Document
import os


class DocumentProcessor:
    """Process and prepare documents for RAG evaluation"""

    def __init__(self, document_path: str):
        self.document_path = Path(document_path)
        self.documents: List[Document] = []

        if not self.document_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")

    def load_document(self) -> List[Document]:
        """Load document based on file type"""
        file_extension = self.document_path.suffix.lower()

        if file_extension == '.pdf':
            return self._load_pdf()
        elif file_extension == '.txt':
            return self._load_txt()
        elif file_extension in ['.docx', '.doc']:
            return self._load_docx()
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def _load_pdf(self) -> List[Document]:
        """Load PDF document"""
        loader = PyMuPDFLoader(str(self.document_path))
        documents = loader.load()

        # Add metadata
        for i, doc in enumerate(documents):
            doc.metadata.update({
                "page_number": i + 1,
                "source_type": "pdf",
                "file_name": self.document_path.name
            })

        self.documents = documents
        return documents

    def _load_txt(self) -> List[Document]:
        """Load text document"""
        loader = TextLoader(str(self.document_path))
        documents = loader.load()

        # Add metadata
        for doc in documents:
            doc.metadata.update({
                "source_type": "txt",
                "file_name": self.document_path.name
            })

        self.documents = documents
        return documents

    def _load_docx(self) -> List[Document]:
        """Load DOCX document"""
        try:
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(str(self.document_path))
            documents = loader.load()

            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    "source_type": "docx",
                    "file_name": self.document_path.name
                })

            self.documents = documents
            return documents

        except ImportError:
            raise ImportError("docx2txt package is required for DOCX files. Install with: pip install docx2txt")

    def get_document_info(self) -> dict:
        """Get basic information about the loaded document"""
        if not self.documents:
            self.load_document()

        total_chars = sum(len(doc.page_content) for doc in self.documents)

        return {
            "file_name": self.document_path.name,
            "file_type": self.document_path.suffix,
            "num_pages": len(self.documents),
            "total_characters": total_chars,
            "avg_chars_per_page": total_chars // len(self.documents) if self.documents else 0
        }
