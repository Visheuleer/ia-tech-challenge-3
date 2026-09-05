from medical_assistant.database import models  # noqa: F401
from medical_assistant.database.base import Base
from medical_assistant.database.session import engine


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")


if __name__ == "__main__":
    main()