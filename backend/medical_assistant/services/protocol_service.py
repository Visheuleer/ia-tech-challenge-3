from dataclasses import dataclass

from medical_assistant.llm.retriever import (
    ProtocolRetriever,
    get_protocol_retriever,
)


@dataclass
class ProtocolResult:
    content: str
    source: str


class ProtocolService:
    def __init__(
        self,
        retriever: ProtocolRetriever | None = None,
    ) -> None:
        self.retriever = (
            retriever or get_protocol_retriever()
        )

    def search(
        self,
        query: str,
        k: int = 3,
    ) -> list[ProtocolResult]:
        documents = self.retriever.search(
            query=query,
            k=k,
        )

        return [
            ProtocolResult(
                content=document.page_content,
                source=document.metadata.get(
                    "source",
                    "unknown",
                ),
            )
            for document in documents
        ]