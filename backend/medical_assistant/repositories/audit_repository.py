from sqlalchemy import select
from sqlalchemy.orm import Session

from medical_assistant.database.models.audit_log import (
    AuditLog,
)


class AuditRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def list_all(
        self,
    ) -> list[AuditLog]:
        statement = (
            select(AuditLog)
            .order_by(
                AuditLog.created_at.desc()
            )
        )

        return list(
            self.db.scalars(
                statement
            ).all()
        )

    def get_by_id(
        self,
        audit_id: int,
    ) -> AuditLog | None:
        return self.db.get(
            AuditLog,
            audit_id,
        )

    def list_by_patient(
        self,
        patient_id: int,
    ) -> list[AuditLog]:
        statement = (
            select(AuditLog)
            .where(
                AuditLog.patient_id
                == patient_id
            )
            .order_by(
                AuditLog.created_at.desc()
            )
        )

        return list(
            self.db.scalars(
                statement
            ).all()
        )