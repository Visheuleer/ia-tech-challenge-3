from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from medical_assistant.core.config import settings


def load_protocols() -> list[Document]:
    protocols_path = Path(settings.protocols_path)

    if not protocols_path.exists():
        raise FileNotFoundError(
            f"Protocols directory not found: {protocols_path}"
        )

    documents: list[Document] = []

    for file_path in protocols_path.glob("*.md"):
        content = file_path.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": file_path.name,
                    "path": str(file_path),
                },
            )
        )

    if not documents:
        raise RuntimeError(
            f"No protocol documents found in {protocols_path}"
        )

    return documents


def split_documents(
    documents: list[Document],
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
    )

    return splitter.split_documents(documents)


def build_vector_store(
    documents: list[Document],
) -> FAISS:
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
    )

    return FAISS.from_documents(
        documents=documents,
        embedding=embeddings,
    )


def main() -> None:
    documents = load_protocols()

    print(f"Loaded {len(documents)} protocol documents.")

    chunks = split_documents(documents)

    print(f"Generated {len(chunks)} chunks.")

    vector_store = build_vector_store(chunks)

    output_path = Path(settings.vector_store_path)
    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    vector_store.save_local(
        str(output_path)
    )

    print(
        f"Vector store saved successfully to {output_path}."
    )


if __name__ == "__main__":
    main()