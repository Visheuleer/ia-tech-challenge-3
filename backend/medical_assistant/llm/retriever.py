from functools import lru_cache
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from medical_assistant.core.config import settings


class ProtocolRetriever:
    def __init__(self) -> None:
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
        )

        vector_store_path = Path(
            settings.vector_store_path
        )

        if not vector_store_path.exists():
            raise FileNotFoundError(
                "Vector store not found. "
                "Run scripts/build_vector_store.py first."
            )

        self.vector_store = FAISS.load_local(
            folder_path=str(vector_store_path),
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True,
        )

    def search(
        self,
        query: str,
        k: int = 3,
    ) -> list[Document]:
        return self.vector_store.similarity_search(
            query=query,
            k=k,
        )


@lru_cache
def get_protocol_retriever() -> ProtocolRetriever:
    return ProtocolRetriever()