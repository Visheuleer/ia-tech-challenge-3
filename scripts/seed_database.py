from datetime import date, datetime, timedelta

from sqlalchemy import delete

from medical_assistant.database.models import (
    AuditLog,
    BloodPressureMeasurement,
    LabExam,
    MedicalHistory,
    Medication,
    Patient,
)
from medical_assistant.database.session import SessionLocal


def clear_database() -> None:
    with SessionLocal() as session:
        session.execute(delete(AuditLog))
        session.execute(delete(BloodPressureMeasurement))
        session.execute(delete(LabExam))
        session.execute(delete(Medication))
        session.execute(delete(MedicalHistory))
        session.execute(delete(Patient))

        session.commit()


def seed_patients() -> None:
    now = datetime.now()

    with SessionLocal() as session:

        patient_1 = Patient(
            name="Paciente 001",
            birth_date=date(1965, 4, 12),
            sex="Masculino",
            weight_kg=78.0,
            height_cm=174.0,
        )

        session.add(patient_1)
        session.flush()

        session.add_all(
            [
                MedicalHistory(
                    patient_id=patient_1.id,
                    condition="Hipertensão arterial sistêmica",
                    diagnosis_date=date(2018, 3, 15),
                    notes="Paciente em acompanhamento regular.",
                ),
                MedicalHistory(
                    patient_id=patient_1.id,
                    condition="Dislipidemia",
                    diagnosis_date=date(2020, 7, 10),
                    notes="Controle clínico regular.",
                ),
            ]
        )

        session.add_all(
            [
                BloodPressureMeasurement(
                    patient_id=patient_1.id,
                    systolic=126,
                    diastolic=78,
                    measured_at=now - timedelta(days=3),
                ),
                BloodPressureMeasurement(
                    patient_id=patient_1.id,
                    systolic=128,
                    diastolic=80,
                    measured_at=now - timedelta(days=10),
                ),
                BloodPressureMeasurement(
                    patient_id=patient_1.id,
                    systolic=124,
                    diastolic=76,
                    measured_at=now - timedelta(days=18),
                ),
            ]
        )

        session.add(
            Medication(
                patient_id=patient_1.id,
                name="Losartana",
                dosage="50 mg",
                frequency="1 vez ao dia",
                start_date=date(2020, 1, 10),
                active=True,
            )
        )

        session.add_all(
            [
                LabExam(
                    patient_id=patient_1.id,
                    exam_type="Creatinina",
                    result="0.9 mg/dL",
                    reference_range="0.7 - 1.3 mg/dL",
                    status="completed",
                    performed_at=now - timedelta(days=30),
                ),
                LabExam(
                    patient_id=patient_1.id,
                    exam_type="Potássio",
                    result="4.3 mEq/L",
                    reference_range="3.5 - 5.1 mEq/L",
                    status="completed",
                    performed_at=now - timedelta(days=30),
                ),
            ]
        )


        patient_2 = Patient(
            name="Paciente 002",
            birth_date=date(1972, 9, 23),
            sex="Feminino",
            weight_kg=91.0,
            height_cm=165.0,
        )

        session.add(patient_2)
        session.flush()

        session.add_all(
            [
                MedicalHistory(
                    patient_id=patient_2.id,
                    condition="Hipertensão arterial sistêmica",
                    diagnosis_date=date(2019, 6, 5),
                    notes="Controle pressórico irregular nas últimas consultas.",
                ),
                MedicalHistory(
                    patient_id=patient_2.id,
                    condition="Obesidade",
                    diagnosis_date=date(2021, 2, 18),
                    notes="Em acompanhamento clínico.",
                ),
            ]
        )

        session.add_all(
            [
                BloodPressureMeasurement(
                    patient_id=patient_2.id,
                    systolic=152,
                    diastolic=96,
                    measured_at=now - timedelta(days=2),
                ),
                BloodPressureMeasurement(
                    patient_id=patient_2.id,
                    systolic=148,
                    diastolic=94,
                    measured_at=now - timedelta(days=8),
                ),
                BloodPressureMeasurement(
                    patient_id=patient_2.id,
                    systolic=150,
                    diastolic=92,
                    measured_at=now - timedelta(days=15),
                ),
            ]
        )

        session.add(
            Medication(
                patient_id=patient_2.id,
                name="Losartana",
                dosage="50 mg",
                frequency="1 vez ao dia",
                start_date=date(2021, 5, 20),
                active=True,
            )
        )

        session.add_all(
            [
                LabExam(
                    patient_id=patient_2.id,
                    exam_type="Creatinina",
                    result=None,
                    reference_range="0.7 - 1.3 mg/dL",
                    status="pending",
                    performed_at=None,
                ),
                LabExam(
                    patient_id=patient_2.id,
                    exam_type="Potássio",
                    result="4.5 mEq/L",
                    reference_range="3.5 - 5.1 mEq/L",
                    status="completed",
                    performed_at=now - timedelta(days=45),
                ),
            ]
        )


        patient_3 = Patient(
            name="Paciente 003",
            birth_date=date(1958, 1, 30),
            sex="Masculino",
            weight_kg=86.0,
            height_cm=170.0,
        )

        session.add(patient_3)
        session.flush()

        session.add_all(
            [
                MedicalHistory(
                    patient_id=patient_3.id,
                    condition="Hipertensão arterial sistêmica",
                    diagnosis_date=date(2015, 8, 12),
                    notes="Histórico de dificuldade no controle pressórico.",
                ),
                MedicalHistory(
                    patient_id=patient_3.id,
                    condition="Diabetes mellitus tipo 2",
                    diagnosis_date=date(2017, 11, 22),
                    notes="Em tratamento e acompanhamento clínico.",
                ),
                MedicalHistory(
                    patient_id=patient_3.id,
                    condition="Doença renal crônica em acompanhamento",
                    diagnosis_date=date(2024, 3, 14),
                    notes="Necessita acompanhamento periódico de função renal.",
                ),
            ]
        )

        session.add_all(
            [
                BloodPressureMeasurement(
                    patient_id=patient_3.id,
                    systolic=182,
                    diastolic=112,
                    measured_at=now - timedelta(days=1),
                ),
                BloodPressureMeasurement(
                    patient_id=patient_3.id,
                    systolic=176,
                    diastolic=108,
                    measured_at=now - timedelta(days=5),
                ),
                BloodPressureMeasurement(
                    patient_id=patient_3.id,
                    systolic=170,
                    diastolic=104,
                    measured_at=now - timedelta(days=12),
                ),
            ]
        )

        session.add_all(
            [
                Medication(
                    patient_id=patient_3.id,
                    name="Losartana",
                    dosage="50 mg",
                    frequency="2 vezes ao dia",
                    start_date=date(2022, 4, 10),
                    active=True,
                ),
                Medication(
                    patient_id=patient_3.id,
                    name="Amlodipino",
                    dosage="5 mg",
                    frequency="1 vez ao dia",
                    start_date=date(2023, 9, 15),
                    active=True,
                ),
            ]
        )

        session.add_all(
            [
                LabExam(
                    patient_id=patient_3.id,
                    exam_type="Creatinina",
                    result="1.8 mg/dL",
                    reference_range="0.7 - 1.3 mg/dL",
                    status="completed",
                    performed_at=now - timedelta(days=20),
                ),
                LabExam(
                    patient_id=patient_3.id,
                    exam_type="Potássio",
                    result=None,
                    reference_range="3.5 - 5.1 mEq/L",
                    status="pending",
                    performed_at=None,
                ),
            ]
        )

        session.commit()


def main() -> None:
    clear_database()
    seed_patients()

    print("Database seeded successfully.")


if __name__ == "__main__":
    main()